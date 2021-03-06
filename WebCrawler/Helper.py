class Helper:
    _debug = False

    @staticmethod
    def get_domain(url):
        #print("get_domain")
        i = 0
        tempCharList = []

        # If protocol: skip to the right index
        if 'http://' in url:
            i = 7
        elif 'https://' in url:
            i = 8

        # set protocol and host to lower case
        while(i < len(url)):
           
            if i > 0 and url[i] == '/' and not (url[i - 1] == ':' or url[i - 1] == '/'):
                break

            tempCharList.append(url[i].lower())   
            i += 1

        return ''.join(tempCharList)

    @staticmethod
    def get_path(url):
        # Strip protocol:
        url = url.split('//')[-1]

        # Get the path
        path = '/' + '/'.join(url.split('/')[1:])
        if url[-1:] == '/' and path[-1:] != '/':
            path += '/'

        return path
    @staticmethod
    def set_debug(mode):

        if mode.lower() == 'off':
            Helper._debug = False
        elif mode.lower() == 'on':
            Helper._debug = True
        else:
            print("You didn't change debug mode...")

    @staticmethod
    def debug(string):
        if Helper._debug == True:
            print(    'DEBUG: ' + string)
