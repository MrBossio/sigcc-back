# Generated by Django 3.1.3 on 2023-06-02 23:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('login', '0001_initial'),
        ('capacitaciones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rubricaexamenxempleado',
            name='empleado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee'),
        ),
        migrations.AddField(
            model_name='rubricaexamenxempleado',
            name='rubrica_examen',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.rubricaexamen'),
        ),
        migrations.AddField(
            model_name='rubricaexamen',
            name='learning_path',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.learningpath'),
        ),
        migrations.AddField(
            model_name='rubricaexamen',
            name='rubrica_examen_x_empleado',
            field=models.ManyToManyField(through='capacitaciones.RubricaExamenXEmpleado', to='login.Employee'),
        ),
        migrations.AddField(
            model_name='proveedorusuario',
            name='empresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.proveedorempresa'),
        ),
        migrations.AddField(
            model_name='proveedorusuario',
            name='habilidad_x_proveedor_usuario',
            field=models.ManyToManyField(through='capacitaciones.HabilidadXProveedorUsuario', to='capacitaciones.Habilidad'),
        ),
        migrations.AddField(
            model_name='proveedorempresa',
            name='categoria',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.categoria'),
        ),
        migrations.AddField(
            model_name='preguntaxcursoudemy',
            name='pregunta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.pregunta'),
        ),
        migrations.AddField(
            model_name='habilidadxproveedorusuario',
            name='habilidad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.habilidad'),
        ),
        migrations.AddField(
            model_name='habilidadxproveedorusuario',
            name='proveedor_usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.proveedorusuario'),
        ),
        migrations.AddField(
            model_name='empleadoxlearningpath',
            name='empleado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee'),
        ),
        migrations.AddField(
            model_name='empleadoxlearningpath',
            name='learning_path',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.learningpath'),
        ),
        migrations.AddField(
            model_name='empleadoxcursoxpreguntaxalternativa',
            name='alternativa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.alternativa'),
        ),
        migrations.AddField(
            model_name='empleadoxcursoxpreguntaxalternativa',
            name='empleado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee'),
        ),
        migrations.AddField(
            model_name='empleadoxcursoxpreguntaxalternativa',
            name='pregunta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.pregunta'),
        ),
        migrations.AddField(
            model_name='empleadoxcursoxlearningpath',
            name='curso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursogeneral'),
        ),
        migrations.AddField(
            model_name='empleadoxcursoxlearningpath',
            name='empleado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee'),
        ),
        migrations.AddField(
            model_name='empleadoxcursoxlearningpath',
            name='learning_path',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.learningpath'),
        ),
        migrations.AddField(
            model_name='empleadoxcursoempresa',
            name='empleado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee'),
        ),
        migrations.AddField(
            model_name='empleadoxcurso',
            name='curso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursogeneral'),
        ),
        migrations.AddField(
            model_name='empleadoxcurso',
            name='empleado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee'),
        ),
        migrations.AddField(
            model_name='documentorespuesta',
            name='empleado_learning_path',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.empleadoxlearningpath'),
        ),
        migrations.AddField(
            model_name='documentoexamen',
            name='learning_path',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.learningpath'),
        ),
        migrations.AddField(
            model_name='detallerubricaexamenxempleado',
            name='detalle_rubrica_examen',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.detallerubricaexamen'),
        ),
        migrations.AddField(
            model_name='detallerubricaexamenxempleado',
            name='empleado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee'),
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
        migrations.AddField(
            model_name='cursogeneralxlearningpath',
            name='curso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursogeneral'),
        ),
        migrations.AddField(
            model_name='cursogeneralxlearningpath',
            name='learning_path',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.learningpath'),
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
        migrations.AddField(
            model_name='asistenciasesionxempleado',
            name='empleado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.employee'),
        ),
        migrations.AddField(
            model_name='asistenciasesionxempleado',
            name='sesion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.sesion'),
        ),
        migrations.AddField(
            model_name='alternativa',
            name='pregunta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.pregunta'),
        ),
        migrations.AddField(
            model_name='sesion',
            name='cursoEmpresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursoempresa'),
        ),
        migrations.AddField(
            model_name='preguntaxcursoudemy',
            name='curso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursoudemy'),
        ),
        migrations.AddField(
            model_name='pregunta',
            name='pregunta_x_curso',
            field=models.ManyToManyField(through='capacitaciones.PreguntaXCursoUdemy', to='capacitaciones.CursoUdemy'),
        ),
        migrations.AddField(
            model_name='empleadoxcursoxpreguntaxalternativa',
            name='curso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursoudemy'),
        ),
        migrations.AddField(
            model_name='empleadoxcursoempresa',
            name='cursoEmpresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursoempresa'),
        ),
        migrations.AddField(
            model_name='cursoempresa',
            name='curso_empresa_x_empleado',
            field=models.ManyToManyField(through='capacitaciones.EmpleadoXCursoEmpresa', to='login.Employee'),
        ),
        migrations.AddField(
            model_name='asistenciasesionxempleado',
            name='curso_empresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capacitaciones.cursoempresa'),
        ),
    ]