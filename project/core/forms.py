"""
.. topic:: **Envios (formulários)**

"""

# forms.py na pasta demandas

from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField

# form para redefinir dias atrás para a data de referência
class data_ref_Form(FlaskForm):

    dias_atras = IntegerField('Qtd dias para a data de referência')
    submit = SubmitField('Registrar')


