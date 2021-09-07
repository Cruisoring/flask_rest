from flask import Flask, json, render_template, abort, request, flash, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField, validators
from wtforms.validators import DataRequired, Regexp
import markdown.extensions.fenced_code
from data_helper import load_content, save_content
from dynamic import Dynamic
from mock import Mockings, Mock, DYNAMIC_ROUTES
from dotenv import load_dotenv, find_dotenv
from deepdelta import DeepDelta
from urllib.parse import unquote


load_dotenv(find_dotenv())

api = Flask(__name__)
api.config['SECRET_KEY'] = 'secretkey'
rules = []


@api.route('/')
def home():
  readme_file = open('README.md', 'r')
  help = markdown.markdown(
      readme_file.read(), extensions=["fenced_code"]
  )
  
  return render_template('home.html', readme=help)

@api.route('/api/token')
def getToken():
  res = Dynamic.from_json('external/token_response.json')
  return res


@api.route('/security/internal/login', methods=['GET', 'POST'])
def getLogin():
  res = Dynamic.from_json('external/login_response.json')
  return res


@api.route('/routes')
def routes():

  if len(rules) == 0:
    for rule in api.url_map.iter_rules():
      options = {}
      for arg in rule.arguments:
          options[arg] = "[{0}]".format(arg)

      methods = ','.join(rule.methods)
      url = unquote(url_for(rule.endpoint, **options))
      rules.append((url, methods, rule.endpoint))

    rules.sort(key=lambda r: r[0])

  return render_template('routes.html', rules=rules, mocks=DYNAMIC_ROUTES)

class CompareForm(FlaskForm):
  left = TextAreaField("Left Object")
  right = TextAreaField("Right Object")
  submit = SubmitField("Submit")


@api.route('/compare', methods=['GET', 'POST'])
def compare():
  form = CompareForm()

  if request.method == 'GET':
    return render_template('compare.html', form=form)
  elif request.method == 'POST':
    left = json.loads(request.form.get('left'))
    right = json.loads(request.form.get('right'))
    delta = DeepDelta.compare(left, right)
    flash(json.dumps(delta, indent=4), 'success')
    return render_template('compare.html', form=form)
  else:
    abort()


@api.route('/api/compare', methods=['POST'])
def compare_api():
  payload = json.loads(request.data)
  left = payload['left']
  right = payload['right']
  delta = DeepDelta.compare(left, right)
  return delta


class CreateForm(FlaskForm):
  data_file = FileField('Data File:')
  route = StringField('Route:', validators=[DataRequired()])
  key = StringField('Key Name:', validators=[DataRequired()])
  submit = SubmitField("Submit")


@api.route('/create', methods=['GET', 'POST'])
def create():
  form = CreateForm()

  if request.method == 'POST':
    upload_file = request.files['data_file']
    if form.validate_on_submit():
      file_name = upload_file.filename
      upload_file.save(f"data/{file_name}")
      key_name = request.form.get('key')
      route = request.form.get('route')
      result = Mock.add_dynamic(file_name, key_name, route)
      return redirect(url_for('routes'))

  return render_template('create.html', form=form)


@api.route('/api/admin/routes/new', methods=['POST'])
def routes_new():
 
  payload = Dynamic.as_dynamic(json.loads(request.data))
  file_name = payload.fileName
  content = payload.content
  key_name = payload.keyName
  route = payload.route
  save_content(file_name, content)
  return Mock.add_dynamic(file_name, key_name, route)


@api.route('/api/', defaults={'path': ''})
@api.route('/api/<path:path>', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH', 'HEAD', 'OPTIONS'])
def catch_all(path):
    return Mock.handle_default(path)


def single_file_handler(file_or_path: str) -> callable:
  data = load_content(file_or_path)    

  def handler(key):
    if data == None:
      abort(404)

    result = data.replace('"key"', key)
    if request.method == 'GET':
      return result, 200
    elif request.method == 'DELETE':
      return result, 202
    else:
      return result, 201    
  
  return handler

mappings = {}

def load_routes(f: str = None):
  mappings_file = f or 'mappings.json'
  with open(mappings_file, 'r') as json_file:
    try:
        mappings = json.load(json_file)
    except Exception:
        return None

  for mapping in mappings['collection_mappings']:
    padded = mapping + [None, None]
    Mock.add_dynamic(padded[0], padded[1], padded[2])

  for mapping in mappings['single_mappings']:
    try:
      padded = mapping + [None, None, None, None]
      route, file_path, name, options, *rest = padded
      func = single_file_handler(file_path)
      options = options or {}
      api.add_url_rule(route, name or route, func, **options)  
    except:
      print(f"Failed to load mapping of {mapping}")

load_routes()
print(api.url_map._rules)

if __name__ == '__main__':  
  
  api.run(host="0.0.0.0", port=8000, debug=True)

