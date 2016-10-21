# -*- coding: utf-8 -*-

import sys, random
from PyQt4 import QtGui, QtCore, uic
from enum import Enum
from xmlrpc.server import SimpleXMLRPCServer

MainWindowUI, MainWindowBase = uic.loadUiType("servidor.ui")

class Dir(Enum):
	ARRIBA = 1
	ABAJO = 2
	IZQ = 3
	DER = 4

class Estado(Enum):
	EN_MARCHA = 5
	PAUSADO = 6
	REANUDAR = 7
	NINGUNO = 8

class Servidor(QtGui.QMainWindow):

	def __init__(self):
		super( Servidor, self ).__init__()
		uic.loadUi( 'servidor.ui', self )
		self.termina_juego.hide()
		self.estado = Estado.EN_MARCHA
		self.timer = QtCore.QTimer( self )
		self.snakes_bebes = []
		self.redimensionar()
		self.poner_lienzo_celdas()
		self.clickers()
		self.tabla.setSelectionMode( QtGui.QTableWidget.NoSelection )
    	#self.principal.setWidgetResizable(True)


	def redimensionar( self ):
		self.tabla.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		self.tabla.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)


	def poner_lienzo_celdas( self ):
		self.tabla.setSelectionMode(QtGui.QTableWidget.NoSelection)
		for i in range( self.tabla.rowCount() ) :
			for j in range( self.tabla.columnCount() ) :
				self.tabla.setItem( i, j, QtGui.QTableWidgetItem() )
				self.tabla.item( i, j ).setBackground( QtGui.QColor( 0, 0, 0 ) )


	def clickers( self ):
		self.columnas.valueChanged.connect( self.cambio_numero_celdas )
		self.filas.valueChanged.connect( self.cambio_numero_celdas )
		self.espera.valueChanged.connect( self.actualizar_espera )
		self.estado_juego.clicked.connect( self.estado_del_juego )
		self.termina_juego.clicked.connect( self.terminar_juego )


	def estado_del_juego( self ):
		if self.estado == Estado.EN_MARCHA:
			self.iniciar_juego()
			self.estado = Estado.PAUSADO
		elif self.estado == Estado.PAUSADO:
			self.pausar_juego()
			self.estado = Estado.REANUDAR
		else:
			self.reanudar_juego()
			self.estado = Estado.PAUSADO


	def cambio_numero_celdas( self ):
		filas = self.filas.value()
		columnas = self.columnas.value()
		self.tabla.setRowCount(filas)
		self.tabla.setColumnCount(columnas)
		self.poner_lienzo_celdas()
		self.redimensionar()


	def actualizar_espera( self ):
		mili_seg = self.espera.value()
		self.timer.setInterval(mili_seg)


	def iniciar_juego( self ):
		self.termina_juego.show()
		self.estado_juego.setText( "PAUSAR JUEGO" )
		self.snakes_bebes.append(Snake())
		self.dibuja_snakes_bebes()
		self.timer.timeout.connect( self.mueve_snakebb )
		self.timer.start( self.espera.value() )
		self.tabla.installEventFilter( self )
	

	def pausar_juego( self ):
		self.estado_juego.setText( "REANUDAR JUEGO" )
		self.timer.stop()
	

	def reanudar_juego( self ):
		self.estado_juego.setText( "PAUSAR JUEGO" )
		self.timer.start()


	def terminar_juego( self ):
		self.termina_juego.hide()
		self.estado = Estado.EN_MARCHA
		self.estado_juego.setText( "INICIAR JUEGO" )
		self.snakes_bebes = []
		self.timer.stop()
		self.poner_lienzo_celdas()


	def dibuja_snakes_bebes( self ):
		for snake_bb in self.snakes_bebes:
			snake_bb.pintate_de_colores(self.tabla)


	def eventFilter( self, source, event ):
		if event.type() == QtCore.QEvent.KeyPress and source is self.tabla :
			teclita = event.key()

			if teclita == QtCore.Qt.Key_Up and source is self.tabla:
				for snake_bb in self.snakes_bebes:
					if snake_bb.direccion is not Dir.ABAJO:
						snake_bb.direccion = Dir.ARRIBA

			if teclita == QtCore.Qt.Key_Down and source is self.tabla:
				for snake_bb in self.snakes_bebes:
					if snake_bb.direccion is not Dir.ARRIBA:
						snake_bb.direccion = Dir.ABAJO

			if teclita == QtCore.Qt.Key_Right and source is self.tabla:
				for snake_bb in self.snakes_bebes:
					if snake_bb.direccion is not Dir.IZQ:
						snake_bb.direccion = Dir.DER

			if teclita == QtCore.Qt.Key_Left and source is self.tabla:
				for snake_bb in self.snakes_bebes:
					if snake_bb.direccion is not Dir.DER:
						snake_bb.direccion = Dir.IZQ

		return QtGui.QMainWindow.eventFilter( self, source, event )


	def autocanibal_snake( self, snake ):
		for cachito_snake in snake.cuerpo_snake[:len(snake.cuerpo_snake)-2]:
			if snake.cuerpo_snake[-1][0] == cachito_snake[0] and snake.cuerpo_snake[-1][1] == cachito_snake[1]:
				#ponermensajito
				return True
		return False


	def mueve_snakebb( self ):
		for snake_bb in self.snakes_bebes:
			if self.autocanibal_snake( snake_bb ): # :'c
				self.snakes_bebes.remove( snake_bb )
				self.poner_lienzo_celdas()
				snake_bebesita = Snake()
				self.snakes_bebes.append(snake_bebesita)
			self.tabla.item( snake_bb.cuerpo_snake[0][0], snake_bb.cuerpo_snake[0][1] ). setBackground( QtGui.QColor( 0, 0, 0 ) )
			chachito = 0

			for cachito_snake_bb in snake_bb.cuerpo_snake[ :len( snake_bb.cuerpo_snake )-1 ]:
				chachito += 1
				cachito_snake_bb[0] = snake_bb.cuerpo_snake[chachito][0]
				cachito_snake_bb[1] = snake_bb.cuerpo_snake[chachito][1]

			if snake_bb.direccion == Dir.ARRIBA:
				if snake_bb.cuerpo_snake[-1][0] != 0:
					snake_bb.cuerpo_snake[-1][0] -= 1
				else:
					snake_bb.cuerpo_snake[-1][0] = self.tabla.rowCount()-1

			if snake_bb.direccion == Dir.ABAJO:
				if snake_bb.cuerpo_snake[-1][0]+1 < self.tabla.rowCount():
					snake_bb.cuerpo_snake[-1][0] += 1
				else:
					snake_bb.cuerpo_snake[-1][0] = 0

			if snake_bb.direccion == Dir.DER:
				if snake_bb.cuerpo_snake[-1][1]+1 < self.tabla.columnCount():
					snake_bb.cuerpo_snake[-1][1] += 1
				else:
					snake_bb.cuerpo_snake[-1][1] = 0

			if snake_bb.direccion == Dir.IZQ:
				if snake_bb.cuerpo_snake[-1][1] != 0:
					snake_bb.cuerpo_snake[-1][1] -= 1
				else:
					snake_bb.cuerpo_snake[-1][1] = self.tabla.columnCount()-1

		self.dibuja_snakes_bebes()


	def conexion( self ):
		servidor = SimpleXMLRPCServer( ( "localhost", self.puerto ) )


class Snake():
	def __init__( self ):
		self.cuerpo_snake = [[0,0],[1,0],[2,0],[3,0],[4,0]]
		self.tamanio = len( self.cuerpo_snake )
		self.direccion = Dir.ABAJO
		self.R, self.G, self.B = map( int, colores_bonis().split(" ") )


	def pintate_de_colores( self, tabla ):
			for cachito_snake_bb in self.cuerpo_snake:
				tabla.item( cachito_snake_bb[0], cachito_snake_bb[1] ).setBackground( QtGui.QColor( self.R, self.G, self.B ) )


def colores_bonis():
	R=G=B=0
	
	R = random.randint( 10, 255 )
	G = random.randint( 10, 255 )
	B = random.randint( 10, 255 )
	return str(R)+" "+str(G)+" "+str(B)


app = QtGui.QApplication(sys.argv)
window = Servidor()
window.show()
sys.exit(app.exec_())