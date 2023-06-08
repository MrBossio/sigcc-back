import json
from django.shortcuts import render
from rest_framework import status
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from zappa.asynchronous import task
from rest_framework.exceptions import ValidationError
from django.db.models import Avg
from ..models import Evaluation
from ..serializers import *
from login.serializers import *
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.db.models import F
from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models.aggregates import Sum,Count   
from django.db.models import F, ExpressionWrapper, FloatField
from collections import defaultdict
from rest_framework.permissions import AllowAny


def validate_employee_and_evaluation(employee_id, tipoEva):
    if not employee_id or not tipoEva:
        raise ValidationError("Employee's id and evaluationType are required")

    try:
        employee_id = int(employee_id)
        if employee_id <= 0:
            raise ValueError()
    except ValueError:
        raise ValidationError("Invalid value for employee_id.")

    if not isinstance(tipoEva, str) or not tipoEva.strip():
        raise ValidationError("Invalid value for tipoEva.")

def get_category_averages(evaluations):
    category_scores = EvaluationxSubCategory.objects.filter(evaluation__in=evaluations).values('subCategory__category__name').annotate(avg_score=Avg('score'))
    category_averages = {score['subCategory__category__name']: score['avg_score'] for score in category_scores}
    return category_averages
# Create your views here.
class EvaluationView(generics.ListCreateAPIView):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    
class PositionGenericView(generics.ListCreateAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

class AreaGenericView(APIView):
    def get(self, request):
        area = Area.objects.all()
        area_serializado = AreaSerializer(area,many=True)
        return Response(area_serializado.data,status=status.HTTP_200_OK)

    def post(self,request):
        area_serializado = AreaSerializer(data = request.data)

        if area_serializado.is_valid():
            area_serializado.save()
            return Response(area_serializado.data,status=status.HTTP_200_OK)
        
        return Response(None,status=status.HTTP_400_BAD_REQUEST)

class CategoryGenericView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class EvaluationTypeGenericView(generics.ListCreateAPIView):
    queryset = EvaluationType.objects.all()
    serializer_class = EvaluationTypeSerializer

class SubCategoryTypeGenericView(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

class GetPersonasACargo(APIView):
    def post(self, request):
        supervisor_id = request.data.get("id")
        evaluation_type = request.data.get("evaluationType")
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_final=request.data.get("fecha_final")

        validate_employee_and_evaluation(supervisor_id, evaluation_type)

        personas = Employee.objects.filter(supervisor=supervisor_id)
        evaluation_type_obj = get_object_or_404(EvaluationType, name=evaluation_type)
        evaluations = Evaluation.objects.filter(evaluated__in=personas, evaluationType=evaluation_type_obj, isActive=True, isFinished=True)
        employee_data = []
        category_scores = {}

        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                evaluations = evaluations.filter(evaluationDate__gte=fecha_inicio)
            except ValueError:
                return Response("Invalid value for fecha_inicio.", status=status.HTTP_400_BAD_REQUEST)

        if fecha_final:
            try:
                fecha_final = datetime.strptime(fecha_final, "%Y-%m-%d").date()
                evaluations = evaluations.filter(evaluationDate__lte=fecha_final)
            except ValueError:
                return Response("Invalid value for fecha_final.", status=status.HTTP_400_BAD_REQUEST)

        category_scores = defaultdict(list)
        category_averages = {}

        for evaluation in evaluations:
            responseQuery = EvaluationxSubCategory.objects.filter(evaluation=evaluation)
            dataSerialized = ContinuousEvaluationIntermediateSerializer(responseQuery, many=True)
            subcategories = dataSerialized.data
            for subcategory in subcategories:
                subcategory['evaluationDate'] = evaluation.evaluationDate
                # If this line is confusing, remember subcategory is a record of the EvaluationxSubCategory table
                category_id = subcategory['subCategory']['category']['name']
                score = subcategory['score']
                
                category_scores[category_id].append((score, evaluation.evaluationDate.year, evaluation.evaluationDate.month))  # Append the score, year, and month
                
        # Calculate average score for each category per year and month
        for category_id, scores in category_scores.items():
            category_averages[category_id] = {}
            year_month_scores = defaultdict(list)
            for score, year, month in scores:
                year_month_scores[(year, month)].append(score)
            for (year, month), scores in year_month_scores.items():
                average_score = sum(scores) / len(scores)
                category_averages[category_id][f"{year}-{month:02d}"] = average_score

        for persona in personas:
            # Get the latest evaluation for the specified evaluation type
            evaluation = Evaluation.objects.filter(evaluated=persona, evaluationType=evaluation_type_obj).order_by('-evaluationDate').first()
            
            # Calculate time since last evaluation
            time_since_last_evaluation = None
            dias = None
            if evaluation:
                time_since_last_evaluation = timezone.now().date() - evaluation.evaluationDate.date()
                dias = time_since_last_evaluation.days
            # Construct the desired employee data
            employee_data.append({
                'id': persona.id,
                'name': f"{persona.user.first_name} {persona.user.last_name}",
                'time_since_last_evaluation': dias,
                'area': {
                    'id': persona.area.id,
                    'name': persona.area.name
                },
                'position': {
                    'id': persona.position.id,
                    'name': persona.position.name
                },
                'email': persona.user.email
            })
            
        for employee in employee_data:
            employee['CategoryAverages'] = category_averages

        return Response(employee_data, status=status.HTTP_200_OK)
    
class GetHistoricoDeEvaluaciones(APIView):
    #permission_classes = [AllowAny]
    def post(self, request):
        #request: nivel, fecha_inicio,fecha_final, tipoEva, employee_id
        employee_id = request.data.get("employee_id")
        tipoEva = request.data.get("evaluationType")
        nivel = request.data.get("nivel")
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_final=request.data.get("fecha_final")  
        #print(request.data)
        #pprint.pprint(request.__dict__, stream=sys.stderr)
        #print("employee_id", employee_id)
        #print("EvaType", tipoEva)
        validate_employee_and_evaluation(employee_id, tipoEva)
        
        
        evaType = get_object_or_404(EvaluationType, name=tipoEva)
        query = Evaluation.objects.filter(evaluated_id=employee_id, evaluationType=evaType, isActive=True, isFinished=True)
        
        if nivel:
            query = query.filter(finalScore=nivel)

        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                query = query.filter(evaluationDate__gte=fecha_inicio)
            except ValueError:
                return Response("Invalid value for fecha_inicio.", status=status.HTTP_400_BAD_REQUEST)

        if fecha_final:
            try:
                fecha_final = datetime.strptime(fecha_final, "%Y-%m-%d").date()
                query = query.filter(evaluationDate__lte=fecha_final)
            except ValueError:
                return Response("Invalid value for fecha_final.", status=status.HTTP_400_BAD_REQUEST)

        evaluations = query.all()
        responseData = []
        #Continua
        if evaType.name.casefold() == "Evaluación Continua".casefold():
            category_scores = {}
            for evaluation in evaluations:
                responseQuery = EvaluationxSubCategory.objects.filter(evaluation=evaluation)
                dataSerialized = ContinuousEvaluationIntermediateSerializer(responseQuery, many=True)
                subcategories = dataSerialized.data
                for subcategory in subcategories:
                    subcategory['evaluationDate'] = evaluation.evaluationDate
                    #If this line is confusing, remember subcategory is a record of the EvaluationxSubCategory table
                    category_id = subcategory['subCategory']['category']['name']
                    score = subcategory['score']
                    
                    if category_id not in category_scores:
                        category_scores[category_id] = [score]
                    else:
                        category_scores[category_id].append(score)

                # Calculate average score for each category
                category_averages = {}
                for category_id, scores in category_scores.items():
                    category_averages[category_id] = sum(scores) / len(scores)

                responseData.append({
                    'EvaluationId': evaluation.id,
                    'CategoryName': category_id,
                    'evaluationDate' : evaluation.evaluationDate,
                    'score': evaluation.finalScore
                })
             # Calculate average score for each category across all evaluations
            category_averages = {}
            for category_id, scores in category_scores.items():
                category_averages[category_id] = sum(scores) / len(scores)
            # Update responseData with category averages
            for data in responseData:
                data['CategoryAverages'] = category_averages
        #Desempeño
        elif evaType.name.casefold() == "Evaluación de Desempeño".casefold():
            serializedData = PerformanceEvaluationSerializer(evaluations,many=True)
            responseData= serializedData.data
            
        return Response(responseData, status=status.HTTP_200_OK)

class EvaluationAPI(APIView):
    def get(self, request):
        area = Evaluation.objects.all()
        area_serializado = EvaluationSerializerWrite(area,many=True)
        return Response(area_serializado.data,status=status.HTTP_200_OK, many=True)


    def post(self, request):
        area_serializado = EvaluationSerializerWrite(data = request.data)
        
        if area_serializado.is_valid():
            area_serializado.save()
            return Response(area_serializado.data,status=status.HTTP_200_OK)
        
        return Response(area_serializado.errors,status=status.HTTP_400_BAD_REQUEST)
    
class EvaluationXSubcatAPI(APIView):
    def post(self, request):
        
        
        area_serializado = EvaluationxSubCategorySerializer(data = request.data, many=True)
        
        if area_serializado.is_valid():
            area_serializado.save()
            return Response(area_serializado.data,status=status.HTTP_200_OK)
        
        return Response(area_serializado.errors,status=status.HTTP_400_BAD_REQUEST)
    
class EvaluationLineChart(APIView):
    def post(self,request):

        supervisor_id = request.data.get("id")
        evaluation_type = request.data.get("evaluationType")
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_final=request.data.get("fecha_final")


        if (evaluation_type.casefold() != "Evaluación Continua".casefold() and evaluation_type.casefold() != "Evaluación de Desempeño".casefold()):
            return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)
        
        Datos = EvaluationxSubCategory.objects.filter(evaluation__evaluator__id = supervisor_id,evaluation__evaluationType__name=evaluation_type, evaluation__isActive = True)

        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                Datos = Datos.filter(evaluation__evaluationDate__gte=fecha_inicio)
            except ValueError:
                return Response("Invalid value for fecha_inicio.", status=status.HTTP_400_BAD_REQUEST)
        
        if fecha_final:
            try:
                fecha_final = datetime.strptime(fecha_final, "%Y-%m-%d").date()
                Datos = Datos.filter(evaluation__evaluationDate__lte=fecha_final)
            except ValueError:
                return Response("Invalid value for fecha_final.", status=status.HTTP_400_BAD_REQUEST)
        
        Data_serialiazada = EvaluationxSubCategoryRead(Datos,many=True,fields=('id','score','evaluation','subCategory'))
        
        
        data = Data_serialiazada.data
        #print(data)
        # Transform data into the desired format
        result = {}
        for item in data:
            evaluation_date = item['evaluation']['evaluationDate']
            year = evaluation_date.split('-')[0]
            month = evaluation_date.split('-')[1]

            category_name = item['subCategory']['category']['name']
            score_average = item['score']

            if year not in result:
                result[year] = {}

            if month not in result[year]:
                result[year][month] = {}

            if category_name not in result[year][month]:
                result[year][month][category_name] = []

            result[year][month][category_name].append(score_average)

        # Convert the result into the desired format
        transformed_data = []
        for year, year_data in result.items():
            year_entry = {'year': year, 'month': []}
            for month, month_data in year_data.items():
                month_entry = {'month': month, 'category_scores': []}
                for category_name, scores in month_data.items():
                    average_score = sum(scores) / len(scores)
                    category_entry = {'CategoryName': category_name, 'ScoreAverage': average_score}
                    month_entry['category_scores'].append(category_entry)
                year_entry['month'].append(month_entry)
            transformed_data.append(year_entry)

        # Convert the transformed data into JSON format
        transformed_json = json.dumps(transformed_data, indent=4)


        return Response(transformed_data,status=status.HTTP_200_OK)
        
class PlantillasAPI(APIView):
    def post(self,request):
        plantilla = request.data.get("id")
        evaluation_type = request.data.get("evaluationType")

        if (evaluation_type.casefold() != "Evaluación Continua".casefold() and evaluation_type.casefold() != "Evaluación de Desempeño".casefold()):
            return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)
        
        Datos = PlantillaxSubCategoria.objects.filter(plantilla__id = plantilla,plantilla__evaluationType__name=evaluation_type,plantilla__isActive = True)
        Datos_serializados = PlantillaxSubCategoryRead(Datos,many=True,fields=('id','plantilla','subCategory','nombre'))


        grouped_data = {}
        data = Datos_serializados.data
        for item in data:
            plantilla_id = item['plantilla']['id']
            plantilla_name = item['plantilla']['nombre']
            evaluation_type = item['plantilla']['evaluationType']['name']
            category_id = item['subCategory']['category']['id']
            category_name = item['subCategory']['category']['name']
            subcategory_id = item['subCategory']['id']
            subcategory_name = item['subCategory']['name']
            
            if plantilla_id not in grouped_data:
                grouped_data[plantilla_id] = {
                    'id': plantilla_id,
                    'name': plantilla_name,
                    'evaluationType': evaluation_type,
                    'Categories': []
                }
            
            category_exists = False
            for category in grouped_data[plantilla_id]['Categories']:
                if category['id'] == category_id:
                    category_exists = True
                    category['subcategories'].append({
                        'id': subcategory_id,
                        'name': subcategory_name
                    })
                    break
            
            if not category_exists:
                grouped_data[plantilla_id]['Categories'].append({
                    'id': category_id,
                    'name': category_name,
                    'subcategories': [{
                        'id': subcategory_id,
                        'name': subcategory_name
                    }]
                })

        grouped_data = list(grouped_data.values())

        # Datos_noCategorias = PlantillaxSubCategoria.objects.filter(plantilla__id=plantilla,plantilla__evaluationType__name=evaluation_type)
        # Datos_noCategorias_Serializados = PlantillaxSubCategoryRead(Datos_noCategorias,many=True,fields = ('id','subCategory'))
        # data = Datos_noCategorias_Serializados.data
        # subcategories_list = [item['subCategory']['id'] for item in data]
        


        # subcategories_not_in_plantilla = SubCategory.objects.exclude(id__in = subcategories_list).filter(category__id = data[0]['subCategory']['category']['id'])

        # subcategories_not_in_plantilla_serializada = SubCategorySerializerRead(subcategories_not_in_plantilla,many=True)




        # return Response(subcategories_not_in_plantilla_serializada.data,status=status.HTTP_200_OK)

        return Response(grouped_data,status=status.HTTP_200_OK)

        


class PlantillasEditarVistaAPI(APIView):
    def post(self, request):
        plantilla_id = request.data.get("id")
        evaluation_type = request.data.get("evaluationType")

        if not self.is_valid_evaluation_type(evaluation_type):
            return Response("Invalid value for EvaluationType", status=status.HTTP_400_BAD_REQUEST)

        template = self.get_template(plantilla_id)
        if not template:
            return Response("Template not found", status=status.HTTP_404_NOT_FOUND)

        categories = self.get_categories(template)
        subcategories_not_in_template = self.get_subcategories_not_in_template(template, evaluation_type)

        response_data = self.generate_response_data(template, categories, subcategories_not_in_template)
        return Response(response_data, status=status.HTTP_200_OK)

    def is_valid_evaluation_type(self, evaluation_type):
        valid_types = ["Evaluación Continua", "Evaluación de Desempeño"]
        return evaluation_type and evaluation_type.casefold() in [t.casefold() for t in valid_types]

    def get_template(self, template_id):
        try:
            return Plantilla.objects.get(id=template_id, isActive=True)
        except Plantilla.DoesNotExist:
            return None

    def get_categories(self, template):
        subcategories = PlantillaxSubCategoria.objects.filter(
            plantilla=template,
            plantilla__isActive=True,
            isActive=True
        ).select_related('subCategory__category')

        categories = {}
        for subcategory in subcategories:
            category = subcategory.subCategory.category
            if category not in categories:
                categories[category] = []

            categories[category].append(subcategory.subCategory)

        return categories

    def get_subcategories_not_in_template(self, template, evaluation_type):
        subcategories_in_template = PlantillaxSubCategoria.objects.filter(
            plantilla=template,
            plantilla__evaluationType__name=evaluation_type,
            isActive=True
        ).values_list('subCategory_id', flat=True)

        return SubCategory.objects.exclude(id__in=subcategories_in_template).filter(category__evaluationType__name=evaluation_type)

    def generate_response_data(self, template, categories, subcategories_not_in_template):
        evaluation_type = template.evaluationType.name  # Get the evaluation type from the template

        response_data = {
            'plantilla-id': template.id,
            'plantilla-nombre': template.nombre,
            'Categories': []
        }

        for category, subcategories in categories.items():
            if category.evaluationType.name == evaluation_type:  # Filter categories based on evaluation type
                category_data = {
                    'id': category.id,
                    'name': category.name,
                    'Category-active': category.isActive,
                    'subcategory': [
                        {
                            'id': subcategory.id,
                            'subcategory-isActive': subcategory.isActive,
                            'nombre': subcategory.name
                        }
                        for subcategory in subcategories
                    ]
                }

                response_data['Categories'].append(category_data)

        for subcategory in subcategories_not_in_template:
            category_data = next(
                (category for category in response_data['Categories'] if (category['id'] == subcategory.category.id )),
                None
            )

            if category_data is None:
                category_data = {
                    'id': subcategory.category.id,
                    'name': subcategory.category.name,
                    'Category-active': False,
                    'subcategory': []
                }
                response_data['Categories'].append(category_data)

            subcategory_data = {
                'id': subcategory.id,
                'subcategory-isActive': False,
                'nombre': subcategory.name
            }
            category_data['subcategory'].append(subcategory_data)

        return response_data



        
class VistaCategoriasSubCategorias(APIView):
    def post(self,request):
        #plantilla = request.data.get("id")
        evaluation_type = request.data.get("evaluationType")

        if (evaluation_type.casefold() != "Evaluación Continua".casefold() and evaluation_type.casefold() != "Evaluación de Desempeño".casefold()):
            return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)
        
        Datos = SubCategory.objects.filter(category__evaluationType__name=evaluation_type,isActive = True)
        Datos_serializados = SubCategorySerializerRead(Datos,many=True,fields=('id','name','category'))

        grouped_data = {}
        json_data = Datos_serializados.data
        for item in json_data:
            category_id = item['category']['id']
            category_name = item['category']['name']
            subcategory_id = item['id']
            subcategory_name = item['name']
            
            if category_id not in grouped_data:
                grouped_data[category_id] = {
                    'category-id': category_id,
                    'category-name': category_name,
                    'subcategory': []
                }
            
            grouped_data[category_id]['subcategory'].append({
                'id': subcategory_id,
                'name': subcategory_name
            })

        grouped_data = list(grouped_data.values())

        return Response(grouped_data,status=status.HTTP_200_OK)       
    
class EvaluationLineChartPersona(APIView):
    def post(self,request):

        persona_id = request.data.get("id")
        evaluation_type = request.data.get("evaluationType")
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_final=request.data.get("fecha_final")


        if (evaluation_type.casefold() != "Evaluación Continua".casefold() and evaluation_type.casefold() != "Evaluación de Desempeño".casefold()):
            return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)
        
        Datos = EvaluationxSubCategory.objects.filter(evaluation__evaluated__id = persona_id,evaluation__evaluationType__name=evaluation_type, evaluation__isActive = True)

        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                Datos = Datos.filter(evaluation__evaluationDate__gte=fecha_inicio)
            except ValueError:
                return Response("Invalid value for fecha_inicio.", status=status.HTTP_400_BAD_REQUEST)
        
        if fecha_final:
            try:
                fecha_final = datetime.strptime(fecha_final, "%Y-%m-%d").date()
                Datos = Datos.filter(evaluation__evaluationDate__lte=fecha_final)
            except ValueError:
                return Response("Invalid value for fecha_final.", status=status.HTTP_400_BAD_REQUEST)
        
        Data_serialiazada = EvaluationxSubCategoryRead(Datos,many=True,fields=('id','score','evaluation','subCategory'))
        
        
        data = Data_serialiazada.data
        
        # Transform data into the desired format
        result = {}
        for item in data:
            evaluation_date = item['evaluation']['evaluationDate']
            year = evaluation_date.split('-')[0]
            month = evaluation_date.split('-')[1]

            category_name = item['subCategory']['category']['name']
            score_average = item['score']

            if year not in result:
                result[year] = {}

            if month not in result[year]:
                result[year][month] = {}

            if category_name not in result[year][month]:
                result[year][month][category_name] = []

            result[year][month][category_name].append(score_average)

        # Convert the result into the desired format
        transformed_data = []
        for year, year_data in result.items():
            year_entry = {'year': year, 'month': []}
            for month, month_data in year_data.items():
                month_entry = {'month': month, 'category_scores': []}
                for category_name, scores in month_data.items():
                    average_score = sum(scores) / len(scores)
                    category_entry = {'CategoryName': category_name, 'ScoreAverage': average_score}
                    month_entry['category_scores'].append(category_entry)
                year_entry['month'].append(month_entry)
            transformed_data.append(year_entry)

        # Convert the transformed data into JSON format
        transformed_json = json.dumps(transformed_data, indent=4)


        return Response(transformed_data,status=status.HTTP_200_OK)

class PlantillasEditarAPI(APIView):
    def post(self,request):
        plantilla = request.data.get("plantilla-id")
        nuevanombre = request.data.get("plantilla-nombre")
        Plantilla_basica = Plantilla.objects.get(pk=plantilla)

        if(Plantilla_basica.nombre != nuevanombre ):
            Plantilla_basica.nombre = nuevanombre
            Plantilla_basica.save()

        Datos = PlantillaxSubCategoria.objects.filter(plantilla__id = plantilla,plantilla__isActive = True,isActive=True)
        Datos_serializados = PlantillaxSubCategoryRead(Datos,many=True,fields=('id','plantilla','subCategory','nombre'))
        
        Existe = False
        for item in request.data.get("Categories"):
            for subcat in item["subcategory"]:
                    Existe = False
                    
                    
                    for DataExistente in Datos_serializados.data:
                        
                        if(DataExistente['subCategory']['id'] == subcat["id"]):
                            if(subcat["subcategory-isActive"] == True):
                                print("Sí existe categoría")
                            elif(subcat["subcategory-isActive"] == False):
                                PlantillaxSubCategoria.objects.filter(id=DataExistente['id']).update(isActive = False)
                                
                            Existe = True
                            
                            break;
                    if(Existe == False and subcat["subcategory-isActive"] == True):
                        PlantillaxSubCategoria(
                            nombre = subcat["nombre"],
                            plantilla = Plantilla.objects.get(id= request.data.get("plantilla-id")),
                            subCategory = SubCategory.objects.get(id= subcat["id"])
                        ).save()
                        
            

        return Response("Se ha actualizado correctamente",status=status.HTTP_200_OK)

class PlantillasCrearAPI(APIView):
    def post(self,request):
        
        evaltype = request.data.get("evaluationType")
        if (evaltype.casefold() != "Evaluación Continua".casefold() and evaltype.casefold() != "Evaluación de Desempeño".casefold()):
            return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)
        
        obj_evalty =   EvaluationType.objects.get(name= evaltype)
        print(obj_evalty)
        plantilla_creada = Plantilla(nombre = request.data.get('nombre'),evaluationType = obj_evalty)
        plantilla_creada.save()

        print(plantilla_creada)
        if(plantilla_creada is None):
            return Response("No se ha creado correctamente el objeto plantilla",status=status.HTTP_400_BAD_REQUEST)

        for item in request.data.get("subCategories"):
            subcategoriacrear = PlantillaxSubCategoria(nombre = item["nombre"],plantilla=plantilla_creada,subCategory = SubCategory.objects.get(id = item["id"]))
            subcategoriacrear.save()
            if(subcategoriacrear is None):
                return Response("No se ha creado correctamente el objeto subcategoria",status=status.HTTP_400_BAD_REQUEST)
        
        return Response("Se creó correctamente la plantilla ",status=status.HTTP_200_OK)
    

class PlantillaPorTipo(APIView):
    def post(self,request):
        Data = Plantilla.objects.filter(isActive = True)
        Data_serialazada = PlantillaSerializerRead(Data,many=True,fields = ('id','nombre','evaluationType'))


        result = {}
        data = Data_serialazada.data
        for item in data:
            evaluation_type = item['evaluationType']['name']
            plantilla_id = item['id']
            plantilla_nombre = item['nombre']
            
            if evaluation_type not in result:
                result[evaluation_type] = []
            
            result[evaluation_type].append({"plantilla-id": plantilla_id, "plantilla-nombre": plantilla_nombre})


        return Response(result,status=status.HTTP_200_OK)
    
class GetAreas(APIView):
    def get(self, request):
        areas = Area.objects.values('id', 'name')
        return Response(areas)

class GetCategoriasContinuas(APIView):
    def get(self, request):
        evaluation_type = EvaluationType.objects.get(name='Evaluación Continua')
        categorias = Category.objects.filter(evaluationType=evaluation_type).values('id', 'name')
        return Response(categorias)

class GetCategoriasDesempenio(APIView):
    def get(self, request):
        evaluation_type = EvaluationType.objects.get(name='Evaluación de Desempeño')
        categorias = Category.objects.filter(evaluationType=evaluation_type).values('id', 'name')
        return Response(categorias)
    
class EvaluationLineChartReporte(APIView):
    def post(self,request):

        area_id = request.data.get("area-id")
        category_id = request.data.get("category-id")
        evaluation_type = request.data.get("evaluationType")
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_final=request.data.get("fecha_final")


        if (evaluation_type.casefold() != "Evaluación Continua".casefold() and evaluation_type.casefold() != "Evaluación de Desempeño".casefold()):
            return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)
        
        Datos = EvaluationxSubCategory.objects.filter(evaluation__area__id = area_id, evaluation__evaluationType__name=evaluation_type, subCategory__category__id = category_id, evaluation__isActive = True)

        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                Datos = Datos.filter(evaluation__evaluationDate__gte=fecha_inicio)
            except ValueError:
                return Response("Invalid value for fecha_inicio.", status=status.HTTP_400_BAD_REQUEST)
        
        if fecha_final:
            try:
                fecha_final = datetime.strptime(fecha_final, "%Y-%m-%d").date()
                Datos = Datos.filter(evaluation__evaluationDate__lte=fecha_final)
            except ValueError:
                return Response("Invalid value for fecha_final.", status=status.HTTP_400_BAD_REQUEST)
        
        Data_serialiazada = EvaluationxSubCategoryRead(Datos,many=True,fields=('id','score','evaluation','subCategory'))
        
        
        data = Data_serialiazada.data
        
        # Transform data into the desired format
        result = {}
        for item in data:
            evaluation_date = item['evaluation']['evaluationDate']
            year = evaluation_date.split('-')[0]
            month = evaluation_date.split('-')[1]

            category_name = item['subCategory']['category']['name']
            score_average = item['score']

            if year not in result:
                result[year] = {}

            if month not in result[year]:
                result[year][month] = {}

            if category_name not in result[year][month]:
                result[year][month][category_name] = []

            result[year][month][category_name].append(score_average)

        # Convert the result into the desired format
        transformed_data = []
        for year, year_data in result.items():
            year_entry = {'year': year, 'month': []}
            for month, month_data in year_data.items():
                month_entry = {'month': month, 'category_scores': []}
                for category_name, scores in month_data.items():
                    average_score = sum(scores) / len(scores)
                    category_entry = {'CategoryName': category_name, 'ScoreAverage': average_score}
                    month_entry['category_scores'].append(category_entry)
                year_entry['month'].append(month_entry)
            transformed_data.append(year_entry)

        # Convert the transformed data into JSON format
        transformed_json = json.dumps(transformed_data, indent=4)


        return Response(transformed_data,status=status.HTTP_200_OK)