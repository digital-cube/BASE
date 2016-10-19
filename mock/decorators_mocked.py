@route('/tickets')
@authorized_call()
class Tickets:

    @route()
    @params('name': 'id_user', 'type': sid('u'), 'required': True/False)
    @params('name': 'from', 'type': datetime.datetime, 'reqiired': Ture, 'min': datetime.datetime.strptime('2016-01-01 00:00:00'), 'max': now())
    def get(self, id_user, from)
        pass


@route('/tickets')
@authorized_call()
class Ticket:

    #izbeci url_param_type, tako sto pregledas url i ako ima :id i to u urls automatski je to param type
    @route(':id')
    @params('name': 'id', 'type': sid('t'), 'doc': 'docstr')
    def delete(self, id):
        '''documentation'''
        pass

    @route(':id')
    @params('name': 'id', 'type': sid('g'))
    def get(self, id):
        pass


------------------
