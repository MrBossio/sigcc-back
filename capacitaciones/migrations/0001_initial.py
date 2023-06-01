# Generated by Django 3.1.3 on 2023-06-01 21:15

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoria', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'Categoria',
            },
        ),
        migrations.CreateModel(
            name='CursoGeneral',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=300)),
                ('descripcion', models.CharField(max_length=300)),
                ('duracion', models.DurationField(null=True)),
                ('suma_valoracionees', models.IntegerField(default=0)),
                ('cant_valoraciones', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'CursoGeneral',
            },
        ),
        migrations.CreateModel(
            name='DetalleRubricaExamen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criterio_evaluacion', models.CharField(max_length=200)),
                ('nota_maxima', models.IntegerField()),
            ],
            options={
                'db_table': 'DetalleRubricaExamen',
            },
        ),
        migrations.CreateModel(
            name='Habilidad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('habilidad', models.CharField(max_length=300)),
            ],
            options={
                'db_table': 'Habilidad',
            },
        ),
        migrations.CreateModel(
            name='HabilidadXProveedorUsuario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('habilidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.habilidad')),
            ],
            options={
                'db_table': 'HabilidadXProveedorUsuario',
            },
        ),
        migrations.CreateModel(
            name='LearningPath',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=300)),
                ('descripcion', models.TextField()),
                ('url_foto', models.TextField(null=True)),
                ('suma_valoraciones', models.IntegerField(default=0)),
                ('cant_valoraciones', models.IntegerField(default=0)),
                ('cant_empleados', models.IntegerField(default=0)),
                ('horas_duracion', models.DurationField(default=datetime.timedelta(0))),
                ('cant_intentos_cursos_max', models.IntegerField()),
                ('cant_intentos_evaluacion_integral_max', models.IntegerField()),
                ('estado', models.CharField(choices=[('0', 'Desactivado'), ('1', 'Creado sin Formulario'), ('2', 'Error formulario'), ('3', 'Creado completo')], default='0', max_length=1)),
            ],
            options={
                'db_table': 'LearningPath',
            },
        ),
        migrations.CreateModel(
            name='Parametros',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota_maxima', models.IntegerField()),
                ('nota_minima', models.IntegerField()),
                ('numero_intentos_curso', models.IntegerField()),
                ('numero_intentos_lp', models.IntegerField()),
            ],
            options={
                'db_table': 'Parametros',
            },
        ),
        migrations.CreateModel(
            name='Pregunta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.CharField(max_length=1000)),
            ],
            options={
                'db_table': 'Pregunta',
            },
        ),
        migrations.CreateModel(
            name='ProveedorEmpresa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('razon_social', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=40)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.categoria')),
            ],
            options={
                'db_table': 'ProveedorEmpresa',
            },
        ),
        migrations.CreateModel(
            name='RubricaExamen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=200)),
                ('learning_path', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.learningpath')),
            ],
            options={
                'db_table': 'RubricaExamen',
            },
        ),
        migrations.CreateModel(
            name='Sesion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=1000)),
                ('descripcion', models.CharField(max_length=1000)),
                ('fecha_inicio', models.DateTimeField(null=True)),
                ('fecha_limite', models.DateTimeField(null=True)),
                ('url_video', models.TextField(null=True)),
                ('ubicacion', models.CharField(max_length=400, null=True)),
                ('aforo_maximo', models.IntegerField(null=True)),
            ],
            options={
                'db_table': 'Sesion',
            },
        ),
        migrations.CreateModel(
            name='CursoEmpresa',
            fields=[
                ('cursogeneral_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='capacitaciones.cursogeneral')),
                ('tipo', models.CharField(choices=[('P', 'Presencial'), ('S', 'Virtual sincrono'), ('A', 'Virtual asincrono')], max_length=1)),
                ('es_libre', models.BooleanField(default=False)),
                ('url_foto', models.TextField(null=True)),
                ('fecha_creacion', models.DateTimeField(default=django.utils.timezone.now)),
                ('fecha_primera_sesion', models.DateTimeField(null=True)),
                ('cantidad_empleados', models.IntegerField(default=0)),
                ('porcentaje_asistencia_aprobacion', models.IntegerField(default=100)),
            ],
            options={
                'db_table': 'CursoEmpresa',
            },
            bases=('capacitaciones.cursogeneral',),
        ),
        migrations.CreateModel(
            name='CursoUdemy',
            fields=[
                ('cursogeneral_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='capacitaciones.cursogeneral')),
                ('udemy_id', models.IntegerField()),
                ('course_udemy_detail', models.JSONField()),
            ],
            options={
                'db_table': 'CursoUdemy',
            },
            bases=('capacitaciones.cursogeneral',),
        ),
        migrations.CreateModel(
            name='Tema',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=1000)),
                ('sesion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.sesion')),
            ],
            options={
                'db_table': 'Tema',
            },
        ),
        migrations.CreateModel(
            name='SesionXReponsable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.sesion')),
                ('responsable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.proveedorempresa')),
            ],
            options={
                'db_table': 'SesionXReponsable',
            },
        ),
        migrations.AddField(
            model_name='sesion',
            name='sesion_x_responsable',
            field=models.ManyToManyField(through='capacitaciones.SesionXReponsable', to='capacitaciones.ProveedorEmpresa'),
        ),
        migrations.CreateModel(
            name='RubricaExamenXEmpleado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.IntegerField()),
                ('comentario', models.TextField()),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee')),
                ('rubrica_examen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.rubricaexamen')),
            ],
            options={
                'db_table': 'RubricaExamenXEmpleado',
            },
        ),
        migrations.AddField(
            model_name='rubricaexamen',
            name='rubrica_examen_x_empleado',
            field=models.ManyToManyField(through='capacitaciones.RubricaExamenXEmpleado', to='login.Employee'),
        ),
        migrations.CreateModel(
            name='ProveedorUsuario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombres', models.CharField(max_length=60)),
                ('apellidos', models.CharField(max_length=60)),
                ('email', models.CharField(max_length=100)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.proveedorempresa')),
                ('habilidad_x_proveedor_usuario', models.ManyToManyField(through='capacitaciones.HabilidadXProveedorUsuario', to='capacitaciones.Habilidad')),
            ],
            options={
                'db_table': 'ProveedorUsuario',
            },
        ),
        migrations.AddField(
            model_name='habilidadxproveedorusuario',
            name='proveedor_usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.proveedorusuario'),
        ),
        migrations.CreateModel(
            name='EmpleadoXLearningPath',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('0', 'Sin iniciar'), ('1', 'En progreso'), ('2', 'Completado, sin evaluar'), ('3', 'Completado, evaluado'), ('4', 'Desaprobado')], max_length=30)),
                ('porcentaje_progreso', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('apreciacion', models.TextField(null=True)),
                ('fecha_asignacion', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('fecha_limite', models.DateTimeField(null=True)),
                ('fecha_completado', models.DateTimeField(null=True)),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee')),
                ('learning_path', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.learningpath')),
            ],
            options={
                'db_table': 'EmpleadoXLearningPath',
            },
        ),
        migrations.CreateModel(
            name='EmpleadoXCursoXLearningPath',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('progreso', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('estado', models.CharField(choices=[('0', 'Sin iniciar'), ('1', 'En progreso'), ('2', 'Completado, sin evaluar'), ('3', 'Completado, evaluado'), ('4', 'Desaprobado')], max_length=30)),
                ('nota_final', models.IntegerField()),
                ('cant_intentos', models.IntegerField(default=0)),
                ('fecha_evaluacion', models.DateTimeField()),
                ('ultima_evaluacion', models.BooleanField()),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursogeneral')),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee')),
                ('learning_path', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.learningpath')),
            ],
            options={
                'db_table': 'EmpleadoXCursoXLearningPath',
            },
        ),
        migrations.CreateModel(
            name='EmpleadoXCurso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valoracion', models.IntegerField()),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursogeneral')),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee')),
            ],
            options={
                'db_table': 'EmpleadoXCurso',
            },
        ),
        migrations.CreateModel(
            name='DocumentoRespuesta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_documento', models.TextField()),
                ('empleado_learning_path', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.empleadoxlearningpath')),
            ],
            options={
                'db_table': 'DocumentosRespuesta',
            },
        ),
        migrations.CreateModel(
            name='DocumentoExamen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_documento', models.TextField()),
                ('learning_path', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.learningpath')),
            ],
            options={
                'db_table': 'DocumentoExamen',
            },
        ),
        migrations.CreateModel(
            name='DetalleRubricaExamenXEmpleado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.IntegerField()),
                ('comentario', models.TextField()),
                ('detalle_rubrica_examen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.detallerubricaexamen')),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee')),
            ],
            options={
                'db_table': 'DetalleRubricaExamenXEmpleado',
            },
        ),
        migrations.AddField(
            model_name='detallerubricaexamen',
            name='detalle_rubrica_x_empleado',
            field=models.ManyToManyField(through='capacitaciones.DetalleRubricaExamenXEmpleado', to='login.Employee'),
        ),
        migrations.AddField(
            model_name='detallerubricaexamen',
            name='rubrica_examen',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.rubricaexamen'),
        ),
        migrations.CreateModel(
            name='CursoGeneralXLearningPath',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nro_orden', models.IntegerField()),
                ('cant_intentos_max', models.IntegerField()),
                ('porcentaje_asistencia_aprobacion', models.IntegerField(default=100)),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursogeneral')),
                ('learning_path', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.learningpath')),
            ],
            options={
                'db_table': 'CursoGeneralXLearningPath',
            },
        ),
        migrations.AddField(
            model_name='cursogeneral',
            name='curso_x_employee',
            field=models.ManyToManyField(through='capacitaciones.EmpleadoXCurso', to='login.Employee'),
        ),
        migrations.AddField(
            model_name='cursogeneral',
            name='curso_x_learning_path',
            field=models.ManyToManyField(through='capacitaciones.CursoGeneralXLearningPath', to='capacitaciones.LearningPath'),
        ),
        migrations.CreateModel(
            name='Alternativa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto_alternativa', models.CharField(max_length=1000)),
                ('respuesta_correcta', models.BooleanField(default=0)),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.pregunta')),
            ],
            options={
                'db_table': 'Alternativa',
            },
        ),
        migrations.AddField(
            model_name='sesion',
            name='cursoEmpresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursoempresa'),
        ),
        migrations.CreateModel(
            name='PreguntaXCursoUdemy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.pregunta')),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursoudemy')),
            ],
            options={
                'db_table': 'PreguntaXCursoUdemy',
            },
        ),
        migrations.AddField(
            model_name='pregunta',
            name='pregunta_x_curso',
            field=models.ManyToManyField(through='capacitaciones.PreguntaXCursoUdemy', to='capacitaciones.CursoUdemy'),
        ),
        migrations.CreateModel(
            name='EmpleadoXCursoXPreguntaXAlternativa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alternativa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.alternativa')),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee')),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.pregunta')),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursoudemy')),
            ],
            options={
                'db_table': 'EmpleadoXCursoXPreguntaXAlternativa',
            },
        ),
        migrations.CreateModel(
            name='EmpleadoXCursoEmpresa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('porcentajeProgreso', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('fechaAsignacion', models.DateTimeField(null=True)),
                ('fechaLimite', models.DateTimeField(null=True)),
                ('fechaCompletado', models.DateTimeField(null=True)),
                ('apreciacion', models.CharField(max_length=1000, null=True)),
                ('porcentaje_asistencia_aprobacion', models.IntegerField(default=100)),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee')),
                ('cursoEmpresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursoempresa')),
            ],
            options={
                'db_table': 'EmpleadoXCursoEmpresa',
            },
        ),
        migrations.AddField(
            model_name='cursoempresa',
            name='curso_empresa_x_empleado',
            field=models.ManyToManyField(through='capacitaciones.EmpleadoXCursoEmpresa', to='login.Employee'),
        ),
        migrations.CreateModel(
            name='AsistenciaSesionXEmpleado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado_asistencia', models.CharField(choices=[('P', 'Asistió puntual'), ('T', 'Asistió tarde'), ('N', 'No asistió'), ('J', 'Falta justificada')], max_length=1)),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee')),
                ('sesion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.sesion')),
                ('curso_empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursoempresa')),
            ],
            options={
                'db_table': 'AsistenciaSesionXEmpleado',
            },
        ),
    ]
