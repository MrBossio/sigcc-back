import json
from django.shortcuts import render
import sys
from rest_framework import status
import pprint
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
        print(request.data)
        pprint.pprint(request.__dict__, stream=sys.stderr)
        print("employee_id", employee_id)
        print("EvaType", tipoEva)
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
        print(data)
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
    def post(self,request):
        plantilla = request.data.get("id")
        evaluation_type = request.data.get("evaluationType")

        if (evaluation_type.casefold() != "Evaluación Continua".casefold() and evaluation_type.casefold() != "Evaluación de Desempeño".casefold()):
            return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)
        
        Datos = PlantillaxSubCategoria.objects.filter(plantilla__id = plantilla,plantilla__evaluationType__name=evaluation_type,plantilla__isActive = True,isActive=True)
        Datos_serializados = PlantillaxSubCategoryRead(Datos,many=True,fields=('id','plantilla','subCategory','nombre'))


        Datos_noCategorias = PlantillaxSubCategoria.objects.filter(plantilla__id=plantilla,plantilla__evaluationType__name=evaluation_type,isActive=True)
        Datos_noCategorias_Serializados = PlantillaxSubCategoryRead(Datos_noCategorias,many=True,fields = ('id','subCategory'))
        data = Datos_noCategorias_Serializados.data
        subcategories_list = [item['subCategory']['id'] for item in data]
        
        subcategories_not_in_plantilla = SubCategory.objects.exclude(id__in = subcategories_list)

        subcategories_not_in_plantilla_serializada = SubCategorySerializerRead(subcategories_not_in_plantilla,many=True,fields=('id','category','name','description','code'))
        json1 = Datos_serializados.data
        json2 = subcategories_not_in_plantilla_serializada.data

        result = {}

        # Process plantilla from json1
        plantilla = json1[0]['plantilla']
        result['plantilla-id'] = plantilla['id']
        result['plantilla-nombre'] = plantilla['nombre']

        # Process categories and subcategories from json1
        categories = []
        for item in json1:
            category = item['subCategory']['category']
            subcategory = item['subCategory']
            
            # Check if the category already exists in the result
            category_exists = False
            for cat in categories:
                if cat['id'] == category['id']:
                    category_exists = True
                    cat['subcategory'].append({
                        'id': subcategory['id'],
                        'subcategory-isActive': True,
                        'nombre': subcategory['name']
                    })
                    break
            
            # If the category doesn't exist, create it along with its subcategory
            if not category_exists:
                categories.append({
                    'id': category['id'],
                    'name': category['name'],
                    'Category-active': True,
                    'subcategory': [{
                        'id': subcategory['id'],
                        'subcategory-isActive': True,
                        'nombre': subcategory['name']
                    }]
                })

        result['Categories'] = categories

        merged_json = result.copy()
        categories = merged_json["Categories"]
        
        for item in json2:
            category = item["category"]
            subcategory_id = item["id"]
            subcategory_exists = False
            
            # Check if the category already exists in the merged JSON
            for cat in categories:
                if cat["id"] == category["id"]:
                    subcategory_exists = True
                    subcategory = {
                        "id": subcategory_id,
                        "subcategory-isActive": False,
                        "nombre": item["name"]
                    }
                    cat["subcategory"].append(subcategory)
                    break
            
            # If the category doesn't exist, create it with the new subcategory
            if not subcategory_exists:
                new_category = {
                    "id": category["id"],
                    "name": category["name"],
                    "Category-active": False,
                    "subcategory": [
                        {
                            "id": subcategory_id,
                            "subcategory-isActive": False,
                            "nombre": item["name"]
                        }
                    ]
                }
                categories.append(new_category)
            

        return Response(merged_json,status=status.HTTP_200_OK)

        
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
        print(data)
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

        Datos = PlantillaxSubCategoria.objects.filter(plantilla__id = plantilla,plantilla__isActive = True,isActive=True)
        Datos_serializados = PlantillaxSubCategoryRead(Datos,many=True,fields=('id','plantilla','subCategory','nombre'))
        print(Datos_serializados.data)
        Existe = False
        for item in request.data.get("Categories"):
            for subcat in item["subcategory"]:
                    Existe = False
                    
                    print(subcat["id"])
                    for DataExistente in Datos_serializados.data:
                        
                        if(DataExistente['subCategory']['id'] == subcat["id"]):
                            if(subcat["subcategory-isActive"] == True):
                                print("Sí existe categoría")
                            elif(subcat["subcategory-isActive"] == False):
                                PlantillaxSubCategoria.objects.filter(id=DataExistente['id']).update(isActive = False)
                                print("Se elimina la subcategoria de la plantilla")
                            Existe = True
                            print("Se encontró subcat")
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
        #plantilla = request.data.get("plantilla-id")
        evaltype = request.data.get("evaluationType")
        if (evaltype.casefold() != "Evaluación Continua".casefold() and evaltype.casefold() != "Evaluación de Desempeño".casefold()):
            return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)
        print(request.data.get('nombre'))
        plantilla_creada = Plantilla(nombre = request.data.get('nombre'),evaluationType = EvaluationType.objects.get(name= evaltype)).save()

        if(plantilla_creada is None):
            return Response("No se ha creado correctamente el objeto plantilla",status=status.HTTP_400_BAD_REQUEST)
        
        for item in request.data.get("subcategories"):
            subcategoriacrear = PlantillaxSubCategoria(nombre = item["nombre"],plantilla=plantilla_creada,SubCategory = SubCategory.objects.get(id = item["id"])).save()
            if(subcategoriacrear is None):
                return Response("No se ha creado correctamente el objeto subcategoria",status=status.HTTP_400_BAD_REQUEST)
        
        return Response("Se creó correctamente",status=status.HTTP_200_OK)
    

class PlantillaPorTipo(APIView):
    def post(self,request):

        return Response("Se ha actualizado correctamente",status=status.HTTP_200_OK)
    
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