import os.path as path
import configparser as cp
from os import system as sys
from datetime import date, timedelta
from time import sleep as slp
from ftplib import FTP
import shutil
import logging
import logging.handlers
logger=logging.getLogger('Monitoreo de venta')
#https://www.lawebdelprogramador.com/codigo/Python/2214-Crear-un-fichero-de-log-y-rotarlo-por-tiempo.html
#generador de log
logger.setLevel(logging.DEBUG)
handler = logging.handlers.TimedRotatingFileHandler(filename='file.log', when="m", interval=1, backupCount=5)
formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
#fecha
today = date.today()
ayer = today - timedelta(days=1) #Se estrae el calcula de fecha ayer
try:
#parametro de configuracion
    #parametro de configuracion
    configuracion = cp.ConfigParser()
    configuracion.read('conf.cfg')
    carpetaCompartida = configuracion['modoEjecucion']['carpetaCompartida']
    codigo = configuracion['General']['codigo']
    numpc = configuracion['General']['numpc']
    tiempoSlep = int(configuracion['General']['slep'])
    #codigo_maquina_.txt
    archivoU0Z = codigo+"_%s_U0Z.txt"%numpc
    archivoS1 = codigo+"_%s_S1.txt"%numpc
    modoEjecucion = int(configuracion['modoEjecucion']['modo'])

    rutaFtp = configuracion['PathFTP']['rutaFile']
    logger.info('Archivo U0Z y S1 creado satifactoriamente')

except Exception as e:
    logger.warning(str(e))
    #exit()#si no consigue archivo de configuracion cierra el programa

def conexionFTP():
    try:
        global rutaFtp
        ftp = FTP('ftp.cocaisystem.com')
        ftp.login('cocaisys','mE]hX9aW6X32b+')
        ftp.cwd(rutaFtp)
        estatusCftp=True
    except Exception as e:
        print(e)
        logger.warning('error al conecrar al servidor ftp '+str(e))
        estatusCftp=False
    return {'ftp':ftp,'estatusCftp':estatusCftp}
#fecha de ejecucion al archivo de configuracionn rtn string fecha

def stFcfha():
    global configuracion
    configuracion.read('conf.cfg')
    configuracion.set('FeEjecucion', 'fecha', str(today))
    with open("conf.cfg", "w+") as configfile:configuracion.write(configfile);configfile.close()
    return configuracion['FeEjecucion']['fecha']
#activa IntTFHKA.exe para generar los reportes
def activarIntTFHKA():#retorna bool
    try:
        #global ayer,today
        #if (ayer.day<10 ):dia="0"+str(ayer.day)
        #else:dia=str(ayer.day)
        #if (ayer.month<10 ):mes="0"+str(ayer.month)
        #f_ayer=dia+mes+str(ayer.year)
        #fecha_ayer = f_ayer+f_ayer
        #sys("IntTFHKA.exe UploadReportCmd(U2z %s)" % fecha_ayer)
        #sys("IntTFHKA.exe UploadStatusCmd(S1)")
        sys("IntTFHKA.exe UploadReportCmd(U0z)")
        sys("IntTFHKA.exe UploadStatusCmd(S1)")
        statusIntTFHKA = True
        logger.info('Programa ejecutado correctamente!')
    except Exception as e:
        logger.warning(str(e))
        statusIntTFHKA = False
    return statusIntTFHKA

def getStatusIntTFHKA():#retorna bool
    try:
        getStatus = open("Stat_Err.txt", "r+").read()
        getStatus=getStatus[0:5].strip()
        if(len(getStatus) == 4):getStatusIntTFHKA = True
        else:getStatusIntTFHKA = False
    except Exception as e:logger.warning(str(e))
    return getStatusIntTFHKA

#lectura de los archivos y registro de archivo para el servidor ftp
#c/wc U0Z
def cwU0Z():
    try:
        global archivoU0Z
        U0Z_ftp = open(archivoU0Z, "a+")
        #contenido_U0Z = U0Z_ftp.rd()
        final_de_U0Z_ftp = U0Z_ftp.tell()
        listaU0Z = ['%s'% open("Reporte.txt", "r+").read()]
        U0Z_ftp.writelines(listaU0Z)
        U0Z_ftp.seek(final_de_U0Z_ftp)
        cwU0Z=True
    except Exception as e:
        logger.warning(str(e))
        cwU0Z=False
    return cwU0Z

def cwS1():
    try:
        global archivoS1
        S1_ftp = open(archivoS1, "a+")
        #contenido_S1 = S1_ftp.rd()
        final_de_S1_ftp = S1_ftp.tell()
        listaS1 = ['%s'% open("Status.txt", "r+").read()]
        S1_ftp.writelines(listaS1)
        S1_ftp.seek(final_de_S1_ftp)
        cwS1=True
    except Exception as e:logger.warning(str(e));cwS1=False
    return cwS1
#U0Z
def pubU0Z():
    try:
        global archivoU0Z
        fileU0Z = str(archivoU0Z)
        file = open(fileU0Z,'rb')
        if(conexionFTP()['ftp'].storbinary('STOR %s' % fileU0Z, file)):StatusPubU0Z=True
        else:StatusPubU0Z=True
        file.close()
        logger.info("U0Z publicado al ftp")
        conexionFTP()['ftp'].quit()
    except Exception as e:logger.warning(str(e))
    return StatusPubU0Z

def pubS1():
    try:
        global archivoS1
        fileS1 = str(archivoS1)
        file = open(fileS1,'rb')
        if(conexionFTP()['ftp'].storbinary('STOR %s' % fileS1, file)):StatusPubS1=True
        else:StatusPubS1=True
        file.close()
        conexionFTP()['ftp'].quit()
        logger.info("S1 publicado al ftp")
    except Exception as e:logger.warning(str(e))
    return StatusPubS1

def copiaCCU0Z():
    try:
        global archivoU0Z,carpetaCompartida
        fileU0Z = str(archivoU0Z)
        if (path.exists(fileU0Z)):
            shutil.copy(fileU0Z, carpetaCompartida)
            logger.info("U0z copiado a a la carpeta compartida")
            StatusPubU0Z=True
        else:StatusPubU0Z=False
    except Exception as e:
        logger.warning(str(e))
        StatusPubU0Z=False
    return StatusPubU0Z

def copiaCCS1():
    try:
        global archivoS1,carpetaCompartida
        fileS1 = str(archivoS1)
        if (path.exists(fileS1)):
            shutil.copy(fileS1, carpetaCompartida)
            StatusPubS1=True
            logger.info("S1 copiado a a la carpeta compartida")
        else:StatusPubS1=False
    except Exception as e:
        StatusPubS1=False
        logger.warning(str(e))
    return StatusPubS1




def pubCCU0Z():
    try:
        global archivoU0Z
        fileU0Z = str(archivoU0Z)
        file = open(fileU0Z,'rb')
        if (path.exists(fileU0Z)):
            if(conexionFTP()['ftp'].storbinary('STOR %s' % fileU0Z, file)):StatusPubU0Z=True
            else:StatusPubU0Z=True
            file.close()
            logger.info("U0Z publicado al ftp")
            conexionFTP()['ftp'].quit()
        else:StatusPubU0Z=False
    except Exception as e:logger.warning(str(e))
    return StatusPubU0Z

def pubCCS1():
    try:
        global archivoS1
        fileS1 = str(archivoS1)
        if (path.exists(fileS1)):
            file = open(fileS1,'rb')
            if(conexionFTP()['ftp'].storbinary('STOR %s' % fileS1, file)):StatusPubS1=True
            else:StatusPubS1=True
            file.close()
            conexionFTP()['ftp'].quit()
            logger.info("S1 publicado al ftp")
            StatusPubS1=False
    except Exception as e:
        StatusPubS1=False
        logger.warning(str(e))
    return StatusPubS1

def main ():
    global ayer,today,tiempoSlep,archivoU0Z,archivoS1
    slp(tiempoSlep)
    try:
        enviado =False
        if (activarIntTFHKA()):
                logger.info('Programa IntTFHKA activado ')
                if (getStatusIntTFHKA()):
                    logger.critical('impresora conectada satfactoriamente ')
                    if (cwU0Z() and cwS1()):
                        logger.info('Archivo U0Z y S1 crdo satifactoriamente')
                        if conexionFTP()['estatusCftp']:
                            logger.info('conexiona ftp co el servidor en sincronia ')

                            if (pubU0Z() and pubS1()):
                                #conexionFTP()['ftp'].delete(archivoU0Z)
                                #conexionFTP()['ftp'].delete(archivoS1)
                                #conexionFTP()['ftp'].retrlines('LIST')
                                conexionFTP()['ftp'].quit()
                                logger.critical('archivo publicado al servidor ftp satfactoriamente ')
                                enviado = True
                                print("main modo 1 Exito")

                            else:
                                enviado = False
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
    global ayer,today,tiempoSlep,archivoU0Z,archivoS1
    slp(tiempoSlep)
    try:
        enviado =False
        if (copiaCCS1() and copiaCCU0Z()):
            logger.info('Archivo U0Z y S1 creado satifactoriamente')
            if (copiaCCU0Z() and copiaCCS1()):

                logger.info('Archivo U0Z y S1 copiado a la carpeta compartida satifactoriamente')
                enviado = True
            else:
                enviado = False
                print("Error al copiar archivo U0Z y S1")
        else:print("Error al escribir U0Z y S1")
    except Exception as e:logger.warning(str(e))
    return enviado
def mainTres():
    global tiempoSlep,archivoU0Z,archivoS1
    slp(tiempoSlep)
    try:
        enviado =False
        if (pubCCS1() and pubCCU0Z()):
            logger.info('Archivo U0Z y S1 publicado a la carpeta compartida satifactoriamente')
            enviado =True
        else:
            enviado = False
            print("Error al copiar archivo U0Z y S1")
    except Exception as e:logger.warning(str(e))
    return enviado


def intento():
    ejecute=1
    while ejecute > 0:
        if main():
            logger.info('Ejecucion exioso al intento{'     + str(ejecute)+'}')
        else:
            logger.warning('error en jecucion al intento{' + str(ejecute)+'}')
        ejecute+=1
        if ejecute == 5:#numeros de intentos
            break

#comprobamos el modo de ejecuccion
def intentoDos():
    global tiempoSlep
    ejecute=1
    while ejecute > 0:
        if mainDos():
            logger.info('Ejecucion exioso al intento{'     + str(ejecute)+'}')
        else:
            logger.warning('error en jecucion al intento{' + str(ejecute)+'}')
        ejecute+=1
        slp(tiempoSlep)
        if ejecute == 5:#numeros de intentos
            break

def intentoTres():
    ejecute=1
    while ejecute > 0:
        if mainTres():
            logger.info('Ejecucion exioso al intento{'     + str(ejecute)+'}')
        else:
            logger.warning('error en jecucion al intento{' + str(ejecute)+'}')
        ejecute+=1
        slp(tiempoSlep)
        if ejecute == 5:#numeros de intentos
            break
def modoUno():
    if main():
        fechaEjecu=stFcfha()
        while (True):
            if (str(fechaEjecu)==str(date.today())):pass
            else:
                fechaEjecu=date.today()
                if main():
                    logger.critical('Archivo U0Z y S1 pulicado con exito! dia '+today+'reporte dia '+ayer)
                    stFcfha()
                else:
                    intento()
    else:intento()

def modoDos():
    if mainDos():
        fechaEjecu=stFcfha()
        while (True):
            if (str(fechaEjecu)==str(date.today())):pass
            else:
                fechaEjecu=date.today()
                if mainDos():
                    logger.critical('Archivo U0Z y S1 pulicado con exito! dia '+today+'reporte dia '+ayer)
                    stFcfha()
                else:
                    intentoDos()
    else:intentoDos()

def modoTres():
    if mainTres():
        fechaEjecu=stFcfha()
        while (True):
            if (str(fechaEjecu)==str(date.today())):
                pass
            else:
                fechaEjecu=date.today()
                if mainTres():
                    logger.critical('Archivo U0Z y S1 pulicado con exito! dia '+today+'reporte dia '+ayer)
                    stFcfha()
                else:print("error modo 3")
    else:intentoTres()

if modoEjecucion ==1:modoUno()
if modoEjecucion ==2:modoDos()
if modoEjecucion ==3:modoTres()
if (modoEjecucion > 3  or  modoEjecucion < 0):
    logger.warning('Error archivo de configuracion')
    exit()



