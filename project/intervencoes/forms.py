"""

.. topic:: intervencoes (formulários)

   Formulários de intervenções.

"""

# forms.py dentro de convenios

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class CPFForm(FlaskForm):

   cpf_consulta = StringField('CPF para cosulta:')
   
   submit = SubmitField('Pesquisar')
