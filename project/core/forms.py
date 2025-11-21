"""
.. topic:: **Envios (formulários)**

"""

# forms.py na pasta demandas

from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField

# form para redefinir dias atrás para a data de referência
# class data_ref_Form(FlaskForm):

#     dias_atras = IntegerField('Qtd dias para a data de referência')
#     submit = SubmitField('Registrar')

class data_ref_Form(FlaskForm):
    
    data_referencia = DateField('Data de referência',format='%Y-%m-%d', validators=[DataRequired(message='Informe a data de referência!')])
    submit = SubmitField('Registrar')

