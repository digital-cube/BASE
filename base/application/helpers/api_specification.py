import inspect
import importlib
from src.config.app_config import imports as app_imports

def get_api_specification(request_handler):

    # for h in request_handler.application.handlers[0][1]:
    #     hc = h.handler_class
    #     print('Handler', hc, type(hc))
    #     if hasattr(hc, '__API_DOCUMENTATION__'):
    #         print('NASHO DOCS', hc.__API_DOCUMENTATION__)
    #     if hasattr(hc, '__API_DOCUMENTATION2__'):
    #         print('NASHO DOCS2', hc.__API_DOCUMENTATION2__)
    #
    #     for _method in ['get', 'post', 'put', 'patch', 'delete']:
    #         if hasattr(hc, _method):
    #             _m = getattr(hc, _method)
    #             if hasattr(_m, '__API_DOCUMENTATION__'):
    #                 _d = getattr(_m, '__API_DOCUMENTATION__')
    #             if hasattr(_m, '__API_DOCUMENTATION2__'):
    #                 _d = getattr(_m, '__API_DOCUMENTATION2__')

    # for _m in app_imports:
    #     print('Loading {} module'.format(_m))
    #     app_module = importlib.import_module(_m)   #                 print('NASHO DOCS', _d)
    #     for _name, _handler in inspect.getmembers(app_module):
    #
    #         if hasattr(_handler, '__API_DOCUMENTATION__'):
    #             print('NASHO')
    #         print('DIR H', dir(_handler))
            # if inspect.isclass(_handler) and hasattr(_handler, '__URI__'):
            #     print('uchitan', _name)
                #
                # for _method in ['get', 'post', 'put', 'patch', 'delete']:
                #     if hasattr(_handler, _method):
                #         _m = getattr(_handler, _method)
                #         print('DIR', dir(_m))
                        # if hasattr(_m, '__API_DOCUMENTATION__'):
                        #     _d = getattr(_m, '__API_DOCUMENTATION__')
                        #     print(_method, _d)

    return {}
