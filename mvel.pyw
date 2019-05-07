import os.path as path
import configparser as cp
from traceback import format_exc as formErro
from subprocess import call as spc
from os import system as sys
from os import remove as rm
from os import mkdir as mk
from datetime import date, timedelta
from time import sleep as slp
from ftplib import FTP
from shutil import copy as copy
#import shutil
import logging
import logging.handlers
#ver
#https://stackoverflow.com/questions/4438020/how-to-start-a-python-file-while-windows-starts



ifExi  = lambda archivo:path.exists(archivo)#si exsiste los archivo dependiente
spcall = lambda exe:spc(exe, shell=False)#ejecuta subProce



rmvelRgdit="""REG ADD \"HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\" /V \"Rebootmv\" /t REG_SZ /F /D \"C:\\IntTFHKA\\runmvel.exe\""""
conf          =  'conf.cfg'
txtStImp      =  'Stat_Err.txt'
Ru0z          =  'Reporte.txt'
Rs1           =  'Status.txt'#
log           =  'log' #carpeta
uoz           =  'uoz.exe'#ejecutable al llamar
reIntento     = 30

try:

    spcall(rmvelRgdit)
    spcall(uoz)
    if not path.exists(log):mk(log)
    logger    = logging.getLogger('Monitoreo de venta mvel')
    logger.setLevel(logging.DEBUG)
    handler   = logging.handlers.TimedRotatingFileHandler(filename='log/file.log', when="m", interval=1, backupCount=5)
    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%d-%m-%y %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    #fecha
    today = date.today()
    infoERR       = True
    #ayer  = today - timedelta(days=1) #Se estrae el calcula de fecha
    #parametro de configuracion
    configuracion   =   cp.ConfigParser()
    if (ifExi(conf)):
        configuracion.read(conf)
        carpetaCompartida   = configuracion['modoEjecucion']['carpetaCompartida']
        modoEjecucion       = int(configuracion['modoEjecucion']['modo'])
        rutaFtp             = configuracion['PathFTP']['rutaFile']
        codigo              = configuracion['General']['codigo']
        numpc               = configuracion['General']['numpc']
        activacion          = int(configuracion['General']['activacion'])
        tiempoSlep          = int(configuracion['General']['slep'])

        #nombre salida archivoinfoERR       = True
        archivoU0Z          = codigo+"_%s_U0Z.txt"%numpc
        archivoS1           = codigo+"_%s_S1.txt"%numpc

    else:
        confTxt = open(conf, "w+")
        final_de_confTxt = confTxt.tell()
        conftxt="""[General]\ncodigo = set\nnumpc = set\nslep = 1\nactivacion=1\n\n[PathFTP]\nrutafile = /ftpruta\n\n[FeEjecucion]\nfecha = \n\n[modoEjecucion]\nmodo = 1\ncarpetacompartida = temp"""
        confTxt.writelines(conftxt)
        confTxt.seek(final_de_confTxt)
        confTxt.close()
        logger.warning("Aarchivo de conf ya encuentra disponible ")
        exit()
except Exception as e:
    if infoERR == True:
        logger.warning(formErro)
    logger.warning(str(e))
    #exit()#si no consigue archivo de configuracion cierra el programa


def conexionFTP():
    estatusCftp=0
    while True:
        try:
            global rutaFtp,tiempoSlep
            ftp = FTP('ftp.cocaisystem.com')
            ftp.login('cocaisys','mE]hX9aW6X32b+')
            ftp.cwd(rutaFtp)
            estatusCftp = True

        except Exception as e:
            global infoERR
            if infoERR == True:
                logger.warning(formErro)
            logger.warning('Error al conectar al servidor ftp '+str(e))
            estatusCftp  =  False

        if estatusCftp == True:break
        else:slp(tiempoSlep)
    return {'ftp':ftp,'estatusCftp':estatusCftp}



#fecha de ejec ucion al archivo de configuracionn rtn string fecha

def stFcfha():
    global configuracion,conf
    configuracion.read(conf)
    configuracion.set('FeEjecucion', 'fecha', str(today))
    with open(conf, "w+") as configfile:configuracion.write(configfile);configfile.close()
    return configuracion['FeEjecucion']['fecha']
#activa IntTFHKA.exe para generar los reportes

def activarIntTFHKA():#retorna bool
    try:
        global uoz,txtStImp
        if ifExi(uoz):
            spcall(uoz)#ejecuto el ouz.exe
            slp(6)
            if ifExi(txtStImp):
                getSta    = open(txtStImp, "r+").read()
                getStatus = getSta[0:5].strip()
                #getSta.close()
                if(len(getStatus)    ==  4):
                    logger.info('Impresora conectada...')
                    estado  =  True
                    rm(txtStImp)#borro archivo impresora
                else:
                    estado=False
                    logger.warning('Error de impresora')
        else:logger.warning('Programa no se ouz.exe encuentra disponible' );exit()
    except Exception as e:
        global infoERR
        if infoERR == True:
            logger.warning(formErro)
        logger.warning(str(e))
    return estado

#lectura de los archivos y registro de archivo para el servidor ftp
#c/wc U0Z

def cwU0Z():
    try:
        global archivoU0Z,Ru0z
        U0Z_ftp          = open(archivoU0Z, "a+")
        final_de_U0Z_ftp = U0Z_ftp.tell()
        if ifExi(Ru0z):
            slp(2)
            uozNew   = open(Ru0z, "r+").read()
            listaU0Z = ['%s \n'% str(uozNew)]
            U0Z_ftp.writelines(listaU0Z)
            U0Z_ftp.seek(final_de_U0Z_ftp)
            uozNew.close()
            rm(Ru0z)
            estado   = True
        U0Z_ftp.close()
        slp(2)

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
        if ifExi(Rs1      ):
            slp(2)
            final_de_S1_ftp = S1_ftp.tell()
            s1New=open(Rs1      , "r+").read()
            listaS1         = ['%s \n'%s1New ]
            S1_ftp.writelines(listaS1)
            S1_ftp.seek(final_de_S1_ftp)
            s1New.close()
            rm(Ru0z)
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
#U0Z

def pubU0Z():
    try:
        global archivoU0Z
        fileU0Z = str(archivoU0Z)
        file    = open(fileU0Z,'rb')
        if(conexionFTP()['ftp'].storbinary('STOR %s' % fileU0Z, file)):StatusPubU0Z  =  True
        else:StatusPubU0Z  =  False
        file.close()
        logger.info("U0Z publicado al ftp")
        conexionFTP()['ftp'].quit()
    except Exception as e:
        global infoERR
        if infoERR == True:
            logger.warning(formErro)
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
        global archivoS1,carpetaCompartida
        fileS1  =  str(archivoS1)
        if (path.exists(fileS1)):
            copy(fileS1, carpetaCompartida)
            #shutil.copy(fileS1, carpetaCompartida)
            StatusPubS1  =  True
            logger.info("S1 copiado a a la carpeta compartida")
        else:StatusPubS1 =False
    except Exception as e:
        global infoERR
        if infoERR == True:
            logger.warning(formErro)

        logger.warning(str(e))
    return StatusPubS1

def pubCCU0Z():
    try:
        global archivoU0Z
        fileU0Z  =  str(archivoU0Z)
        file     =  open(fileU0Z,'rb')
        if (path.exists(fileU0Z)):
            if(conexionFTP()['ftp'].storbinary('STOR %s' % fileU0Z, file)):StatusPubU0Z  =  True
            else:StatusPubU0Z  =  True
            file.close()
            logger.info("U0Z publicado al ftp")
            conexionFTP()['ftp'].quit()
        else:StatusPubU0Z  =  False
    except Exception as e:
        global infoERR
        if infoERR == True:
            logger.warning(formErro)

        logger.warning(str(e))
    return StatusPubU0Z

def pubCCS1():
    try:
        global archivoS1
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
        global infoERR
        if infoERR == True:
            logger.warning(formErro)

        StatusPubS1  =  False
        logger.warning(str(e))
    return StatusPubS1

def main():
    global today,tiempoSlep,archivoU0Z,archivoS1,uoz
    slp(tiempoSlep)
    try:
        enviado  =  False
        if (activarIntTFHKA()):
            logger.info('impresora conectada satfactoriamente ')
            if (cwU0Z() and cwS1()):
                logger.info('Archivo U0Z y S1 creado satifactoriamente')
                if conexionFTP()['estatusCftp']:
                    logger.info('conexiona ftp co el servidor en sincronia ')
                    if (pubU0Z() and pubS1()):
                        #conexionFTP()['ftp'].delete(archivoU0Z)
                        #conexionFTP()['ftp'].delete(archivoS1)
                        #conexionFTP()['ftp'].retrlines('LIST')
                        conexionFTP()['ftp'].quit()
                        logger.info('archivo publicado al servidor ftp satfactoriamente ')

                        enviado  = True
                    else:
                        enviado  = False

                else:logger.warning("error de conexion con el servidor ftp ")#podemos intentar hacer otra coso
            else:logger.warning("Error al escribir U0Z y S1")
        else:logger.warning("Error de impresora verifique ")

    except Exception as e:
        global infoERR
        if infoERR == True:
            logger.warning(formErro)

        logger.warning(str(e))
    return enviado

def mainDos():
    global today,tiempoSlep,archivoU0Z,archivoS1,uoz
    slp(tiempoSlep)
    try:
        enviado  =  False
        if (activarIntTFHKA()):
            logger.info('impresora conectada satfactoriamente ')
            if (cwU0Z() and cwS1()):
                logger.info('Archivo U0Z y S1 creado satifactoriamente')
                if (copiaCCS1() and copiaCCU0Z()):
                    logger.info('Archivo U0Z y S1 copiado a la carpeta compartida satifactoriamente')
                    enviado  =  True
                    rm(archivoS1)
                    rm(archivoU0Z)
                else:
                    enviado  =  False
                    logger.warning("Error al escribir U0Z y S1")
            else:logger.warning("Error al escribir U0Z y S1")
        else:logger.warning("Error de conxion con impresora ")
    except Exception as e:
        global infoERR
        if infoERR == True:
            logger.warning(formErro)
        logger.warning(str(e))
    return enviado

def mainTres():
    global tiempoSlep,archivoU0Z,archivoS1
    slp(tiempoSlep)
    try:
        enviado      =  False
        while True:
            if (pubCCS1() and pubCCU0Z()):
                logger.info('Archivo U0Z y S1 publicado a la carpeta compartida satifactoriamente')
                enviado  =  True
                rm(archivoS1)
                rm(archivoU0Z)
                break
            else:
                slp(tiempoSlep)
                logger.warning("Error al copiar archivo U0Z y S1")

    except Exception as e:
        global infoERR
        if infoERR == True:
            logger.warning(formErro)
        logger.warning(str(e))
    return enviado

def modoDebug():
    debug           =  'debug' #carpeta
    if not path.exists(debug):mk(debug)
    logger    = logging.getLogger('Monitoreo de venta mvel')
    logger.setLevel(logging.DEBUG)
    handler   = logging.handlers.TimedRotatingFileHandler(filename='debug/file.log', when="m", interval=1, backupCount=5)
    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%d-%m-%y %H:%M:%S')
    handler.setFormatter(formatter)
if infoERR==True:modoDebug()

def modoUno():
    global reIntento,tiempoSlep
    fechaEjecu  =  stFcfha()
    if main():
        logger.info('Ejcucion exitoxa modo 1!')
        while True:
            if (str(fechaEjecu)  ==  str(date.today())):slp(30000+tiempoSlep)
            else:fechaEjecu       =  date.today();stFcfha();modoUno()
    else:
        for i in range(reIntento+1):
            slp(30000+tiempoSlep)
            if i == reIntento:logger.warning('Error en jecucion en systema intento '+str(i));exit()
            logger.warning('Error en jecucion en systema intento '+str(i))
            modoUno()

def modoDos():
    global reIntento,tiempoSlep
    fechaEjecu  =  stFcfha()
    if mainDos():
        logger.info('Ejcucion exitoxa! modo 2')
        while True:
            if (str(fechaEjecu)  ==  str(date.today())):slp(30000+tiempoSlep)
            else:fechaEjecu       =  date.today();stFcfha();modoDos()
    else:
        for i in range(reIntento+1):
            slp(30000+tiempoSlep)
            if i == reIntento:logger.warning('Error en jecucion en systema intento '+str(i));exit()
            logger.warning('Error en jecucion en systema intento '+str(i))
            modoDos()

def modoTres():
    global tiempoSlep,reIntento
    fechaEjecu  =  stFcfha()
    if mainTres():
        logger.info('Ejcucion exitoxa! modo 3')
        while (True):
            if (str(fechaEjecu)  ==  str(date.today())):slp(30000+tiempoSlep)
            else:fechaEjecu      =   date.today();stFcfha();modoTres()
    for i in range(reIntento+1):
            slp(30000+tiempoSlep)
            if i == reIntento:logger.warning('Error en jecucion en systema intento '+str(i));exit()
            logger.warning('Error en jecucion en systema intento '+str(i))
            modoTres()


if activacion ==1:
    if modoEjecucion == 1:modoUno()
    if modoEjecucion == 2:modoDos()
    if modoEjecucion == 3:modoTres()
    if (modoEjecucion > 3  or  modoEjecucion < 0):
        logger.warning('Error archivo de configuracion')
        exit()
else:logger.warning('Error archivo de configuracion');exit()
