#################### Graphviz processor ##########################
from MathModule import *
import random
import tempfile
import re
import gv
from spline import *
import time

random.seed()

def GetAttrs(obj):
	attrs={}
	gsym=gv.firstattr(obj)
	while gsym:
		name=gv.nameof(gsym)
		attrs[name]=gv.getv(obj,gsym)
		gsym=gv.nextattr(obj,gsym)
	return attrs

def RemoveSpaces(data):
	i=0
	while 1:
		if i>len(data)-1 or not (data[i]==' ' or data[i]=='\t'):
			break
		i+=1
	return data[i:]

def GetNextElement(data):
	element=''
	i=0
	for i in range(0,len(data),1):
		if data[i]==' ' or data[i]=='\t':
			break
		element+=data[i]
	if i==0:
		return [None,'']
	return [element,RemoveSpaces(data[i:])]

def GetNPoints(data):
	[number_str,data]=GetNextElement(data)
	number=int(number_str)
	ret_points=[]
	for i in range(0,number,1):
		[x_str,data]=GetNextElement(data)
		[y_str,data]=GetNextElement(data)
		x=int(x_str)
		y=int(y_str)
		ret_points.append([x,y])
	return [ret_points,RemoveSpaces(data)]

def ConvertData(data):
	if re.compile("\.").search(data):
		return float(data)
	return int(data)

def GetNData(data,number):
	ret_points=[]
	for i in range(0,number,1):
		[x_str,data]=GetNextElement(data)
		x=ConvertData(x_str)
		ret_points.append(x)
	return [ret_points,RemoveSpaces(data)]


def GetNElements(data):
	[number_str,data]=GetNextElement(data)
	number=int(number_str)
	return GetNData(data,number)

def GetNCharacters(data):
	[number_str,data]=GetNextElement(data)
	number=int(number_str)	
	element=data[1:1+number]
	return [element,RemoveSpaces(data[1+number:])]

def ParseXDOTData(data):
	#c 5 -black C 5 -black B 7 1003 4436 1010 4425 1018 4412 1022 4400 1054 4303 1050 4181 1045 4122
	eles=re.compile("[ \t]+").split(data)
	parsed_data={}
	NumPairElesOps=['P','p','L','B','b']

	while 1:
		[command,data]=GetNextElement(data)
		if not command:
			break
		elif command in NumPairElesOps:
			[parsed_data[command],data]=GetNPoints(data)
		elif command=='C' or command=='c' or command=='S':
			[got_string,data]=GetNCharacters(data)
			parsed_data[command]=got_string
		elif command=='E' or command=='e':
			[parsed_data[command],data]=GetNData(data,4)
		elif command=='T':
			[points,data]=GetNData(data,4)
			[got_string,data]=GetNCharacters(data)
			if not parsed_data.has_key(command):
				parsed_data[command]=[]
			parsed_data[command].append([points,got_string])
		elif command=='F':
			[points,data]=GetNData(data,1)
			[got_string,data]=GetNCharacters(data)
			parsed_data[command]=[points,got_string]
	return parsed_data

def MakeLenStr(data,length):
	#if len(data)<length:
	#	return data+(length-len(data))*" "
	return data

def GetGVData(names,map,contents=None,type="xdot",node_shape='record',debug=0,output_graphic_filename=None,aliases=None):
	large_mode=False
	if len(names)>800:
		large_mode=True

	if not aliases:
		aliases={}
	if not node_shape:
		node_shape="record"
	if not contents:
		contents={}
	root_name="Root"
	if len(names)>0:
		root_name=str(names[0])
	g=gv.digraph(root_name)
	layout_alrogithm='dot'
	node_color=None
	if large_mode:
		node_shape='point'
		gv.setv(g,"model","subset")
		layout_alrogithm='neato'
		layout_alrogithm='twopi'
		node_color='red'
		debug=1
	gv.setYinvert(g)
	name2node={}
	edges=[]

	method='plain'
	for name in names:
		if aliases.has_key(name):
			display_name=str(aliases[name])
		else:
			display_name=str(name)

		if method=='plain':
			node_str=''
			if contents.has_key(name):
				for i in range(0,len(contents[name]),1):
					[address,op,[op1,op2],comment]=contents[name][i]
					node_str+=str(op)
					if op1:
						node_str+=" "+str(op1)
					if op2:
						node_str+=" "+str(op2)
					node_str+='\r\n'
				display_name="{"+display_name+"|"+node_str+"}"
			node=gv.node(g,display_name)
			name2node[name]=node
			gv.setv(node,"shape",node_shape)
			if node_color:
				gv.setv(node,"color",node_color)
	
		elif method=='layered': #dirty look
			node_str=''
			if contents.has_key(name):
				for i in range(0,len(contents[name]),1):
					[address,op,[op1,op2],comment]=contents[name][i]
					node_str+="|{"+MakeLenStr(str(op),5)
					if op1:
						node_str+="|"+MakeLenStr(str(op1),5)
					if op2:
						node_str+="|"+MakeLenStr(str(op2),5)
					node_str+='}'
			node=gv.node(g,"{"+display_name+node_str+"}")
			name2node[name]=node
			gv.setv(node,"shape","record")

		elif method=='subgraph': #Too big
			subg=gv.graph(g,'cluster'+display_name)
			gv.setv(subg,"label",display_name)
			gv.setv(subg,"color","black")
	
			node=gv.node(subg,display_name)
			name2node[name]=node
			nodes.append(node)
			gv.setv(node,"shape","record")
	
			node_str=''
			if contents.has_key(name):
				src=node
				for i in range(0,len(contents[name]),1):
					[address,op,[op1,op2],comment]=contents[name][i]
					node_str=hex(address)+"|"+str(op)
					if op1:
						node_str+="|"+str(op1)
					if op2:
						node_str+="|"+str(op2)
					node=gv.node(subg,node_str)
					nodes.append(node)
					gv.setv(node,"shape","record")
					#edge=gv.edge(src,node)
					src=node

	for name in names:
		if map.has_key(name):
			for dst_name in map[name]:
				if name2node.has_key(name) and name2node.has_key(dst_name):
					edge=gv.edge(name2node[name],name2node[dst_name])
					gv.setv(edge,"invis","")
					edges.append([name,dst_name,edge])
	if debug:
		print 'Start layout'
		start_time=time.time()
	gv.layout(g,layout_alrogithm)
	if debug:
		end_time=time.time()
		elapsed_time=end_time-start_time
		print 'End layout',end_time-start_time

	prefix=''
	for i in range(0,5,1):
		prefix+=hex(random.randint(0,9999))
	
	gv.render(g,type,".temp.dat")
	if debug:
		img_filename=prefix+".jpg"
		dot_filename=prefix+".dot"
		print 'writing',img_filename
		gv.render(g,"jpg",img_filename) #For debugging
		gv.render(g,"dot",dot_filename) #For debugging
		print 'done writing',img_filename

	if output_graphic_filename:
		gv.render(g,"jpg",output_graphic_filename) #For debugging

	node_attrs_map={}
	edge_attrs_maps={}
	for name in name2node.keys():
		node_attrs=GetAttrs(name2node[name])
		node_attrs_map[name]=node_attrs

	for [src,dst,edge] in edges:
		line_attrs=GetAttrs(edge)
		if not edge_attrs_maps.has_key(src):
			edge_attrs_maps[src]={}
		edge_attrs_maps[src][dst]=line_attrs

	###### Get maxx,maxy
	maxx=0
	maxy=0
	graph_attrs=GetAttrs(g)
	if graph_attrs.has_key('bb'):
		[x1str,y1str,x2str,y2str]=re.compile(",").split(graph_attrs['bb'])
		x1=int(x1str)
		y1=int(y1str)
		x2=int(x2str)
		y2=int(y2str)
		maxx=x1
		if x2>maxx:
			maxx=x2
		maxy=y1
		if y2>maxy:
			maxy=y2
	maxx+=200
	maxy+=200
	
	return [[maxx,maxy],node_attrs_map,edge_attrs_maps]

#################### End of Graphviz processor ###################
##################################################################