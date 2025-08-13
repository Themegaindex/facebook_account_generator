from flask import Flask, render_template, request
from account_utils import create_mail_tm_account, register_facebook_account

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    try:
        count = int(request.form['count'])
        results = []
        for _ in range(count):
            email, password, first_name, last_name, birthday = create_mail_tm_account()
            if email:
                fb_response = register_facebook_account(email, password, first_name, last_name, birthday)
                results.append({
                    'email': email,
                    'password': password,
                    'name': f"{first_name} {last_name}",
                    'birthday': birthday.strftime('%Y-%m-%d'),
                    'response': fb_response
                })
        return render_template('result.html', results=results)
    except Exception as e:
        return f"حدث خطأ: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
