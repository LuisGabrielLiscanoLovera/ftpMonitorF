"""Extre informacion de la impresora fiscall BIXOLON"""
__author__      = "Luis Liscano
__copyright__   = "Copyright 2019, DHJGR"
__email__ = "luisthemaster3@gmail.com"
__status__ = "Production"
__version__ = "1.0.1"


import os.path as path
import configparser as cp
from os import system as sys
from os import remove as rm
from os import mkdir as mk
from datetime import date, timedelta
from time import sleep as slp
from ftplib import FTP
import shutil
import logging
import logging.handlers


#si exsiste los archivo dependiente
ifExi = lambda archivo:path.exists(archivo)

vbsfile       =  'IntTFHKA.vbs'
vbsfileAu     =  'reboot.vbs'
conf          =  'conf.cfg'
txtStImp      =  'Stat_Err.txt'
reporteTxt    =  'Reporte.txt'
statusTxt     =  'Status.txt'
log           =  'log'


def IntTFHKA():
    global vbsfile,vbsfileAu
    scrpVBS="""REG ADD \"HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\" /V \"Rebootmv\" /t REG_SZ /F /D \"C:\\IntTFHKA\\Reboot.exe\""""
    #sys(scrpVBS)

    if ifExi(vbsfile):pass
    else:
        IntTFHAHiden = open(vbsfile, "w+")
        final_de_IntTFHAHiden = IntTFHAHiden.tell()
        scrpVBS="""Set Suno = WScript.CreateObject("WScript.Shell")\nSuno.Run("IntTFHKA.exe UploadStatusCmd(S1)"), 0, True\n
        Set uceroz = WScript.CreateObject("WScript.Shell")\nuceroz.Run("IntTFHKA.exe UploadReportCmd(U0z)"), 0, True"""
        IntTFHAHiden.writelines(scrpVBS)
        IntTFHAHiden.seek(final_de_IntTFHAHiden)
        IntTFHAHiden.close()

    if ifExi(vbsfileAu):pass
    else:
        AutrVbs = open(vbsfileAu, "w+")
        final_de_AutrVbs = AutrVbs.tell()
        scrpVBS="""Set atr = WScript.CreateObject("WScript.Shell")\natr.Run("reboot.exe"), 0, True\n"""
        AutrVbs.writelines(scrpVBS)
        AutrVbs.seek(final_de_AutrVbs)
        AutrVbs.close()

try:
    IntTFHKA()
    if not path.exists(log):mk(log)
    logger    = logging.getLogger('Monitoreo de venta')
    logger.setLevel(logging.DEBUG)
    handler   = logging.handlers.TimedRotatingFileHandler(filename='log/file.log', when="m", interval=1, backupCount=5)
    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%d-%m-%y %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    #fecha
    today = date.today()
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
        #otro               = configuracion['General']['otro']
        tiempoSlep          = int(configuracion['General']['slep'])
        #print (otro)
        #nombre salida archivo
        archivoU0Z          = codigo+"_%s_U0Z.txt"%numpc
        archivoS1           = codigo+"_%s_S1.txt"%numpc

    else:
        confTxt = open(conf, "w+")
        final_de_confTxt = confTxt.tell()
        conftxt="""[General]\ncodigo = set\nnumpc = set\nslep = 1\n\n[PathFTP]\nrutafile = /ftpruta\n\n[FeEjecucion]\nfecha = \n\n[modoEjecucion]\nmodo = 1\ncarpetacompartida = temp"""
        confTxt.writelines(conftxt)
        confTxt.seek(final_de_confTxt)
        confTxt.close()
        logger.warning("Aarchivo de conf ya encuentra disponible ")
        exit()
except Exception as e:
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
        global vbsfile
        sys(vbsfile)
        #rm(str(vbsfiler)
        statusIntTFHKA = True
        logger.info('Programa IntTFHKA ejecutado correctamente!')
    except Exception as e:
        logger.warning(str(e))
        statusIntTFHKA = False
    return statusIntTFHKA

def getStatusIntTFHKA():#retorna bool
    try:
        global txtStImp,tiempoSlep
        if ifExi(txtStImp):
            getSta    = open(txtStImp, "r+").read()
            getStatus = getSta[0:5].strip()
            if(len(getStatus)    ==  4):getStatusIntTFHKA   =  True
            else:
                while True:
                    if activarIntTFHKA():break
                    else:slp(tiempoSlep)
        else:logger.warning(txtStImp+"error archivo")
    except Exception as e:logger.warning(str(e))
    return getStatusIntTFHKA
#lectura de los archivos y registro de archivo para el servidor ftp
#c/wc U0Z

def cwU0Z():
    try:
        global archivoU0Z,reporteTxt
        U0Z_ftp          = open(archivoU0Z, "a+")
        #contenido_U0Z   = U0Z_ftp.rd()
        final_de_U0Z_ftp = U0Z_ftp.tell()
        listaU0Z = ['%s \n'% open(reporteTxt, "r+").read()]
        U0Z_ftp.writelines(listaU0Z)
        U0Z_ftp.seek(final_de_U0Z_ftp)
        cwU0Z             = True
        U0Z_ftp.close()

    except Exception as e:
        logger.warning(str(e))
        cwU0Z  =  False
        U0Z_ftp.close()
    return cwU0Z

def cwS1():
    try:
        global archivoS1,statusTxt
        S1_ftp  =  open(archivoS1, "a+")
        #contenido_S1 = S1_ftp.rd()
        final_de_S1_ftp = S1_ftp.tell()
        listaS1         = ['%s \n'% open(statusTxt, "r+").read()]
        S1_ftp.writelines(listaS1)
        S1_ftp.seek(final_de_S1_ftp)
        cwS1            =  True
        S1_ftp.close()


    except Exception as e:
        cwS1  =  False
        logger.warning(str(e))
        S1_ftp.close()
    return cwS1
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
    except Exception as e:file.close();logger.warning(str(e))
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
        logger.warning(str(e))
    return StatusPubS1

def copiaCCU0Z():
    try:
        global archivoU0Z,carpetaCompartida
        fileU0Z  =  str(archivoU0Z)
        if (path.exists(fileU0Z)):
            shutil.copy(fileU0Z, carpetaCompartida)
            logger.info("U0z copiado a a la carpeta compartida")
            StatusPubU0Z   =  True
        else:StatusPubU0Z  =  False
    except Exception as e:logger.warning(str(e))
    return StatusPubU0Z

def copiaCCS1():
    try:
        global archivoS1,carpetaCompartida
        fileS1  =  str(archivoS1)
        if (path.exists(fileS1)):
            shutil.copy(fileS1, carpetaCompartida)
            StatusPubS1  =  True
            logger.info("S1 copiado a a la carpeta compartida")
        else:StatusPubS1 =False
    except Exception as e:logger.warning(str(e))
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
    except Exception as e:logger.warning(str(e))
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
        StatusPubS1  =  False
        logger.warning(str(e))
    return StatusPubS1


def main():
    global today,tiempoSlep,archivoU0Z,archivoS1,vbsfile
    slp(tiempoSlep)
    try:
        enviado  =  False
        if (activarIntTFHKA()):
                logger.info('Programa IntTFHKA activado ')
                if (getStatusIntTFHKA()):
                    logger.info('impresora conectada satfactoriamente ')
                    if (cwU0Z() and cwS1()):
                        logger.info('Archivo U0Z y S1 creado satifactoriamente')
                        if conexionFTP()['estatusCftp']:
                            logger.info('conexiona ftp co el servidor en sincronia ')
                            if (pubU0Z() and pubS1()):
                                rm(vbsfile)
                                #conexionFTP()['ftp'].delete(archivoU0Z)
                                #conexionFTP()['ftp'].delete(archivoS1)
                                #conexionFTP()['ftp'].retrlines('LIST')
                                conexionFTP()['ftp'].quit()
                                logger.info('archivo publicado al servidor ftp satfactoriamente ')
                                enviado  = True
                            else:
                                enviado  = False
                                print("Error al publicar archivo U0Z y S1")
                        else:print("error de conexion con el servidor ftp ")#podemos intentar hacer otra coso
                    else:print("Error al escribir U0Z y S1")
                else:
                    #podemos cambiar puerto y reintentar
                    print("Error de conxion con impresora ")
        else:print("error de activacion de los archivos exe!")
    except Exception as e:logger.warning(str(e))
    return enviado

def mainDos():
    global today,tiempoSlep,archivoU0Z,archivoS1
    slp(tiempoSlep)
    try:
        enviado  =  False
        if (activarIntTFHKA()):
            logger.info('Programa IntTFHKA activado ')
            if (getStatusIntTFHKA()):
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
                        print("Error al escribir U0Z y S1")
                else:print("Error al escribir U0Z y S1")
            else:print("Error de conxion con impresora ")
        else:print("error de activacion de los archivos exe!")
    except Exception as e:logger.warning(str(e))
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

    except Exception as e:logger.warning(str(e))
    return enviado


def modoUno():
    fechaEjecu  =  stFcfha()
    while True:
        if main():
            logger.info('Ejcucion exitoxa!')
            while (True):
                if (str(fechaEjecu)  ==  str(date.today())):slp(30000)
                else:fechaEjecu       =  date.today();stFcfha();break
        else:logger.warning('Error en jecucion en systema ')

def modoDos():
    fechaEjecu  =  stFcfha()
    while (True):
        if mainDos():
            logger.info('Ejcucion exitoxa! modo 2')
            while True:
                if (str(fechaEjecu)  ==  str(date.today())):slp(30000)
                else:fechaEjecu       =  date.today();stFcfha();break
        else:logger.warning('Error en jecucion en systema ')

def modoTres():
    fechaEjecu  =  stFcfha()
    while (True):
        if mainTres():
            logger.info('Ejcucion exitoxa! modo 3')
            while (True):
                if (str(fechaEjecu)  ==  str(date.today())):slp(30000)
                else:fechaEjecu      =   date.today();stFcfha();break
        else:logger.warning('Error en jecucion en systema ')

if modoEjecucion == 1:modoUno()
if modoEjecucion == 2:modoDos()
if modoEjecucion == 3:modoTres()
if (modoEjecucion > 3  or  modoEjecucion < 0):
    logger.warning('Error archivo de configuracion')
    exit()
