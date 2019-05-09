###Imports
try:
    import requests
    import os.path as path
    import configparser as cp
    from traceback import format_exc as formErro
    from subprocess import call as spc
    from os import system as sys
    from os import remove as rm
    from os import mkdir as mk
    from os.path import dirname
    from os.path import realpath
    from datetime import date, timedelta
    from time import sleep as slp
    from ftplib import FTP
    from shutil import copy as copy
    import logging
    import logging.handlers
    import getpass
except Exception as e:exit()


try:
    today         = date.today()#fecha
    conf          = 'conf.cfg'
    hostFtp       = 'ftp.cocaisystem.com'
    userFtp       = 'cocaisys'
    passFtp       = 'mE]hX9aW6X32b+'
    Ru0z          = 'Reporte.txt'
    Rs1           = 'Reporte_S1.txt'
    log           = 'log' #carpeta
    uoz           = 'uoz.exe'#ejecutable al llamar
    reIntento     = 30
    infoERR       = False #muestra Err
    ifExi  = lambda archivo:path.exists(archivo)#si exsiste los archivo dependiente
    spcall = lambda exe:spc(exe, shell=False)#ejecuta subProce
    #spcall("""REG ADD \"HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\" /V \"Rebootmv\" /t REG_SZ /F /D \"C:\\IntTFHKA\\runmvel.exe\"""")


    #Archivo registro
    if not path.exists(log):mk(log)
    logger    = logging.getLogger('Monitoreo de venta mvel')
    logger.setLevel(logging.DEBUG)
    mesAnio=str(today.month)+''+str(today.year)
    fileLog ='log/log-%s.log'% str(mesAnio)
    handler   = logging.handlers.TimedRotatingFileHandler(filename=fileLog, when="m", interval=1)
    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%d-%m-%y %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    #archivo de configuracion
    configuracion   =   cp.ConfigParser()
    if (ifExi(conf)):
        configuracion.read(conf)
        carpetaCompartida   = configuracion['modoEjecucion']['carpetaCompartida']
        modoEjecucion       = int(configuracion['modoEjecucion']['modo'])
        rutaFtp             = configuracion['PathFTP']['rutaFile']
        codigo              = configuracion['General']['codigo']
        numpc               = configuracion['General']['numpc']
        activacion          = int(configuracion['General']['activacion'])
        tiempoInit          = int(configuracion['General']['tiempo_init'])
        tiempoErr           = int(configuracion['General']['tiempo_err'])

        #nombre salida archivoinfoERR       = True
        archivoU0Z          = codigo+"_%s_U0Z.txt"%numpc
        archivoS1           = codigo+"_%s_S1.txt"%numpc

    else:cretFileConf()
except Exception as e:
    if infoERR == True:logger.warning(formErro)
    logger.warning(str(e))
    #exit()#si no consigue archivo de configuracion cierra el programa


def startup(file_path):
    USER_NAME = getpass.getuser()
    if file_path == "":
        file_path = dirname(realpath(__file__))
    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
    with open(bat_path + '\\' + "mvel.vbs", "w+") as bat_file:
        vbs='''set objshell = createobject("wscript.shell")\nobjshell.run "%s",vbhide''' % file_path
        bat_file.write(vbs)
#startup("C:\\IntTFHKA\\runmvel.exe")#init de registro

def conexionFTP():
    global reIntento, rutaFtp,tiempoErr,hostFtp,passFtp,userFtp,infoERR
    request = requests.get('http://ftp.cocaisystem.com')
    if request.status_code == 200:
        estatusCftp=False
        ftp =False
        try:
            ftp = FTP('ftp.cocaisystem.com')
            ftp.login('cocaisys','mE]hX9aW6X32b+')
            ftp.cwd(rutaFtp)
            estatusCftp = True

        except Exception as e:
            if infoERR == True:logger.warning(formErro)
            logger.warning('Error al conectar al servidor ftp '+str(e))
    else:
        logger.warning('Error al conectar al servidor Error de internet '+str(e))
        slp(tiempoErr)
        main()
    return {'ftp':ftp,'estatusCftp':estatusCftp}


def stFcfha():
    global configuracion,conf
    configuracion.read(conf)
    configuracion.set('FeEjecucion', 'fecha', str(today))
    with open(conf, "w+") as configfile:configuracion.write(configfile);configfile.close()
    return configuracion['FeEjecucion']['fecha']


def activarIntTFHKA():
    try:
        global uoz,Ru0z,infoERR
        if ifExi(uoz)==False:
            #spcall(uoz)#ejecuto el ouz.exe
            #slp(2)
            if ifExi(Ru0z):
                getSta    = open(Ru0z, "r+").read()
                if(len(getSta)   >=  4):
                    logger.info('Impresora conectada...')
                    estado  =  True
                else:
                    estado  =    False

        else:logger.warning('Programa no se ouz.exe encuentra disponible' );exit()
    except Exception as e:
        if infoERR == True:
            logger.warning(formErro)
        logger.warning(str(e))
    return estado


def cretFileConf():
    confTxt = open(conf, "w+")
    final_de_confTxt = confTxt.tell()
    conftxt="""[General]\n
    codigo = set\n
    numpc = set\n
    tiempo_err = 1\n
    tiempo_init = 1\n
    activacion=1\n\n
    [PathFTP]\n
    portFtp=''
    rutafile = /ftpruta\n\n
    [FeEjecucion]\n
    fecha = \n\n
    [modoEjecucion]\n
    modo = 1\n
    carpetacompartida = temp"""
    confTxt.writelines(conftxt)
    confTxt.seek(final_de_confTxt)
    confTxt.close()
    logger.warning("Aarchivo de conf ya encuentra disponible ")
    slp(30*60)
    main()


def cwU0Z():
    try:
        global archivoU0Z,Ru0z,reIntento,tiempoErr
        estado = False
        U0Z_ftp          = open(archivoU0Z, "a+")
        final_de_U0Z_ftp = U0Z_ftp.tell()
        if ifExi(Ru0z):
            uozNew   = open(Ru0z, "r+").read()
            listaU0Z = ['%s \n'% str(uozNew)]
            U0Z_ftp.writelines(listaU0Z)
            U0Z_ftp.seek(final_de_U0Z_ftp)
            estado   = True
        U0Z_ftp.close()

    except Exception as e:
        global infoERR
        if infoERR == True:
            logger.warning(formErro)
        logger.warning(str(e))
        estado  =  False
        U0Z_ftp.close()
    return estado


def cwS1():
    try:
        global archivoS1,Rs1
        S1_ftp  =  open(archivoS1, "a+")
        if ifExi(Rs1):
            final_de_S1_ftp = S1_ftp.tell()
            listaS1         = ['%s \n'% open(Rs1, "r+").read()]
            S1_ftp.writelines(listaS1)
            S1_ftp.seek(final_de_S1_ftp)
            estado            =  True

        S1_ftp.close()
        slp(2)
    except Exception as e:
        global infoERR
        if infoERR == True:
            logger.warning(formErro)
        estado  =  False
        logger.warning(str(e))
        S1_ftp.close()
    return estado


def pubU0Z():
    try:
        global archivoU0Z,infoERR
        fileU0Z = str(archivoU0Z)
        file    = open(fileU0Z,'rb')
        if(conexionFTP()['ftp'].storbinary('STOR %s' % fileU0Z, file)):StatusPubU0Z  =  True
        else:StatusPubU0Z  =  False
        file.close()
        logger.info("U0Z publicado al ftp")
        conexionFTP()['ftp'].quit()
    except Exception as e:
        if infoERR == True:logger.warning(formErro)
        file.close()
        logger.warning(str(e))
    return StatusPubU0Z


def pubS1():
    try:
        global archivoS1
        fileS1  =  str(archivoS1)
        file    =  open(fileS1,'rb')
        if(conexionFTP()['ftp'].storbinary('STOR %s' % fileS1, file)):StatusPubS1  =  True
        else:StatusPubS1  =  False
        file.close()
        conexionFTP()['ftp'].quit()
        logger.info("S1 publicado al ftp")
    except Exception as e:
        global infoERR
        if infoERR == True:
            logger.warning(formErro)
        logger.warning(str(e))
    return StatusPubS1


def copiaCCU0Z():
    try:
        global archivoU0Z,carpetaCompartida
        fileU0Z  =  str(archivoU0Z)
        if (path.exists(fileU0Z)):
            #shutil.copy(fileU0Z, carpetaCompartida)
            copy(fileU0Z, carpetaCompartida)
            logger.info("U0z copiado a a la carpeta compartida")
            StatusPubU0Z   =  True
        else:StatusPubU0Z  =  False
    except Exception as e:
        global infoERR
        if infoERR == True:
            logger.warning(formErro)


        logger.warning(str(e))
    return StatusPubU0Z


def copiaCCS1():
    try:
        global archivoS1,carpetaCompartida,tiempoErr
        fileS1  =  str(archivoS1)
        if (path.exists(fileS1)):
            copy(fileS1, carpetaCompartida)
            #shutil.copy(fileS1, carpetaCompartida)
            StatusPubS1  =  True
            logger.info("S1 copiado a a la carpeta compartida")
        else:
            slp(tiempoErr)
            copiaCCS1()
            StatusPubS1 =False
    except Exception as e:
        global infoERR
        if infoERR == True:
            logger.warning(formErro)

        logger.warning(str(e))
    return StatusPubS1


def pubCCU0Z():
    try:
        global archivoU0Z,infoERR,tiempoErr
        fileU0Z  =  str(archivoU0Z)
        file     =  open(fileU0Z,'rb')
        if (path.exists(fileU0Z)):
            if(conexionFTP()['ftp'].storbinary('STOR %s' % fileU0Z, file)):StatusPubU0Z  =  True
            else:StatusPubU0Z  =  True
            file.close()
            logger.info("U0Z publicado al ftp")
            conexionFTP()['ftp'].quit()
        else:
            slp(tiempoErr)
            pubCCU0Z()

    except Exception as e:
        if infoERR == True:logger.warning(formErro)
        logger.warning(str(e))
    return StatusPubU0Z


def pubCCS1():
    try:
        global archivoS1,infoERR
        fileS1   =  str(archivoS1)
        if (path.exists(fileS1)):
            file =  open(fileS1,'rb')
            if(conexionFTP()['ftp'].storbinary('STOR %s' % fileS1, file)):StatusPubS1  = True
            else:StatusPubS1  =  True
            file.close()
            conexionFTP()['ftp'].quit()
            logger.info("S1 publicado al ftp")
            StatusPubS1  =  False
    except Exception as e:
        if infoERR == True:logger.warning(formErro)

        StatusPubS1  =  False
        logger.warning(str(e))
    return StatusPubS1


def mainUno():
    global today,tiempoInit,tiempoErr,archivoU0Z,archivoS1,Rs1,Ru0z, reIntento
    slp(tiempoInit)
    try:
        enviado  =  False
        if (activarIntTFHKA()):
            logger.info('impresora conectada satfactoriamente ')
            if (cwU0Z() and cwS1()):
                logger.info('Archivo U0Z y S1 creado satifactoriamente')
                if conexionFTP()['estatusCftp']:
                    logger.info('conexiona ftp con el servidor en sincronia ')
                    if (pubU0Z() and pubS1()):
                        conexionFTP()['ftp'].delete(archivoU0Z)
                        conexionFTP()['ftp'].delete(archivoS1)
                        #conexionFTP()['ftp'].retrlines('LIST')
                        conexionFTP()['ftp'].quit()
                        logger.info('archivo publicado al servidor ftp satfactoriamente ')
                        #rm(Rs1)
                        #rm(Ru0z)

                        enviado  = True

                    else:
                        enviado  = False

                else:
                    for i in range(reIntento):
                        if conexionFTP()['ftp']:mainUno()
                        else:logger.warning("error  con el servidor ftp intento "+str(i));slp(tiempoErr)#

            else:logger.warning("Error al escribir U0Z y S1")
        else:
            for i in range(reIntento):
                if activarIntTFHKA():mainUno()
                else:logger.warning("Error de impresora verifique conecion inento "+str(i))

    except Exception as e:
        global infoERR
        if infoERR == True:
            logger.warning(formErro)

        logger.warning(str(e))
    return enviado


def mainDos():
    global today,tiempoInit,tiempoErr,archivoU0Z,archivoS1,Rs1,Ru0z
    slp(tiempoInit)
    try:
        enviado  =  False
        if (activarIntTFHKA()):
            logger.info('impresora conectada satfactoriamente ')
            if (cwU0Z() and cwS1()):
                logger.info('Archivo U0Z y S1 creado satifactoriamente')
                if (copiaCCS1() and copiaCCU0Z()):
                    logger.info('Archivo U0Z y S1 copiado a la carpeta compartida satifactoriamente')
                    enviado  =  True
                    rm(Rs1)
                    rm(Ru0z)
                else:
                    enviado  =  False
                    logger.warning("Error al escribir U0Z y S1")
            else:logger.warning("Error al escribir U0Z y S1")

        else:
            for i in range(reIntento):
                if activarIntTFHKA():mainDos()
                else:logger.warning("Error de impresora verifique conecion inento "+str(i));slp(tiempoErr)


    except Exception as e:
        global infoERR
        if infoERR == True:
            logger.warning(formErro)
        logger.warning(str(e))
    return enviado


def mainTres():
    global tiempoInit,tiempoErr,archivoU0Z,archivoS1,reIntento
    slp(tiempoInit)
    try:
        enviado      =  False
        if (pubCCS1() and pubCCU0Z()):
            logger.info('Archivo U0Z y S1 publicado a la carpeta compartida satifactoriamente')
            enviado  =  True
            rm(archivoS1)
            rm(archivoU0Z)
        else:
            slp(tiempoErr)
            logger.warning("Error al copiar archivo U0Z y S1")



    except Exception as e:
        global infoERR
        if infoERR == True:
            logger.warning(formErro)
        logger.warning(str(e))
    return enviado


def nexDay():
    global tiempoInit
    fechaEjecu  =  stFcfha()
    while True:
        if (str(fechaEjecu)  ==  str(date.today())):slp(tiempoInit+7200)
        else:fechaEjecu       =  date.today();stFcfha();main()


def modoUno():
    global reIntento,tiempoErr
    if mainUno():
        logger.info('Ejcucion exitoxa modo 1!')
        nexDay()
    else:
        slp(tiempoErr)
        logger.warning('Error en jecucion en systema ')
        nexDay()


def modoDos():
    global reIntento,tiempoErr

    if mainDos():
        logger.info('Ejcucion exitoxa! modo 2')
        nexDay()
    else:
        slp(tiempoErr)
        logger.warning('Error en jecucion en systema')
        modoDos()


def modoTres():
    global tiempoErr,reIntento

    if mainTres():
        logger.info('Ejcucion exitoxa! modo 3')
        nexDay()
    else:
        slp(tiempoErr)
        logger.warning('Error en jecucion en systema intento ')
        modoTres()


def main():
    global activacion, modoEjecucion

    if activacion ==1:
        if modoEjecucion == 1:modoUno()
        if modoEjecucion == 2:modoDos()
        if modoEjecucion == 3:modoTres()
        if (modoEjecucion > 3  or  modoEjecucion < 0):
            logger.warning('Error archivo de configuracion')
            exit()
    else:logger.warning('Error archivo de configuracion');exit()

if __name__ == '__main__':main()




 #ayer  = today - timedelta(days=1) #Se estrae el calcula de fecha
