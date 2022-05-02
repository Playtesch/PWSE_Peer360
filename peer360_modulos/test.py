from urllib.request import urlopen


def test_connection(module):
    production = False
    if not production:
        try:
            if urlopen("http://webservidormais.pythonanywhere.com/{}/test".format(module)).read() != b'OK':
                print("Error: {} has issues!".format(module))
            else:
                print("Connection established to {}".format(module))
        except:
            print("Error: {} unreachable!".format(module))
    else:
        pass


test_connection("modulo_assessment")
test_connection("modulo_bbdd")
test_connection("modulo_cuentas")
test_connection("modulo_email")
test_connection("modulo_export")
test_connection("modulo_forms")
test_connection("modulo_funcionesAux")
test_connection("modulo_uploadFile")
