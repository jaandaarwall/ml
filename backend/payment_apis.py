from flask_restful import Resource
from flask import jsonify, make_response
from flask_security import auth_token_required, roles_required
from .Sqldatabase import db
from .models import Payment

class DummyPaymentAPI(Resource):
    @auth_token_required
    @roles_required('user')
    def post(self, payment_id):
        payment = Payment.query.get_or_404(payment_id)

        payment.status = "Success"
        db.session.commit()

        return make_response(jsonify({
            "message": "Payment successful",
            "amount": payment.amount
        }), 200)
