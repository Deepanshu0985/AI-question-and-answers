from flask import Flask, render_template, request, session, redirect, url_for
# from get_vector import extractJson
import json

app = Flask(__name__)

def extractJson(physics, chemistry, maths, mapping_file):
    """
    Demo function to simulate backend processing.
    It takes three lists (physics, chemistry, maths)
    and returns a JSON summary.
    """

    # Just some mock processing
    result = {
        "summary": {
            "total_subjects": 3,
            "total_questions": len(physics) + len(chemistry) + len(maths)
        },
        "details": {
            "physics": {
                "count": len(physics),
                "questions": physics
            },
            "chemistry": {
                "count": len(chemistry),
                "questions": chemistry
            },
            "maths": {
                "count": len(maths),
                "questions": maths
            }
        }
    }

    # Return a JSON string (for display in template)
    return json.dumps(result, indent=4)

app.secret_key = "supersecretkey"   # Required for using session

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get raw string inputs
        physics_raw = request.form.get('physics')
        chemistry_raw = request.form.get('chemistry')
        maths_raw = request.form.get('maths')
        mapping_file = request.files.get('mapping_file')
        print(mapping_file)

        # Safe JSON parsing
        def safe_load(raw):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return []

        physics = safe_load(physics_raw)
        chemistry = safe_load(chemistry_raw)
        maths = safe_load(maths_raw)

        # Process using your function
        data = extractJson(physics, chemistry, maths,mapping_file)

        # ✅ Store result temporarily in Flask session
        session['result_data'] = data

        # ✅ Redirect to /result (Flask handles it internally)
        return redirect(url_for('result'))

    # Render input form on GET
    return render_template('index.html')


@app.route('/result', methods=['GET', 'POST'])
def result():
    data = session.get('result_data')
    if not data:
        return redirect(url_for('index'))

    if request.method == 'POST':
        test_name = request.form.get('test_name')
        # Simulate saving...
        print(f"✅ Saved '{test_name}' to DB with data: {data}")
        session.pop('result_data', None)
        return render_template('result.html', data=data, success=f"Test '{test_name}' saved successfully!")

    return render_template('result.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)



