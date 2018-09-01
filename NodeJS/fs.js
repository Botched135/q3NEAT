var fs = require('fs');

var csv = require('fast-csv');
var sleep = require('sleep');

var args = process.argv.slice(2);
// generate csv name based on participantID
var ipAddress = args[0]
var participantID = args[1];

//Generate name for csv-file --> REMEMBER TO WRITE 0 
var csvEDA = "CSV/Participant"+participantID+"EDA.csv";
var csvHR = "CSV/Participant"+participantID+"HR.csv";
var csvEDAStream = csv.format({headers: true,delimiter: ';'}),
    writableEDAStream = fs.createWriteStream(csvEDA);
writableEDAStream.on("finish", function(){
  console.log("Wrote to "+csvEDA);
});
csvEDAStream.pipe(writableEDAStream);

var csvHRStream = csv.format({headers: true,delimiter: ';'}),
    writableHRStream = fs.createWriteStream(csvHR);
writableHRStream.on("finish", function(){
  console.log("Wrote to "+csvHR);
});
csvHRStream.pipe(writableHRStream);



var EmpaticaE4 = require('empatica-e4-client');
var dev1 = new EmpaticaE4();

//Declare arrays and makes them 2D
var PhysArray =[];
var PhysTuple = '';

var inCombat = true;
var initTime = "0";
var sensorData = '';
var currentHR = -1;
var currentHRV = -1;
var currentEDA = -1;
var currentIBI = -1;
var previousIBI = 0;


var portNumber  = 755;
var deviceID    = '5F04BC';        //Empatica E4 device ID 

dev1.connect(portNumber ,ipAddress, deviceID, function(data){  
    sensorData = EmpaticaE4.getString(data);
	if(sensorData[0] === 'R')
		return;
	
	var replace = sensorData.replace("\r\n"," ");
	
	replace = replace.replace(",",".");
	var split = replace.split(" ");

	if(initTime === "0")
		initTime= split[1];
	
	if(split[0] === "E4_Gsr")
	{		
		currentEDA = split[2];
		csvEDAStream.write({EDA_Timestamp: ("="+split[1]+"-"+initTime),EDA: currentEDA});
		if(inCombat)
		{
			PhysTuple = new Array(4);
		
			PhysTuple[0] = currentEDA;
			PhysTuple[1] = -1;
			PhysTuple[2] = -1;
			PhysTuple[3] = -1;
			PhysArray.push(PhysTuple);
		}

	}	
	else if(split[0] === "E4_Hr")
	{
		currentHR = split[2];
		console.log(currentHR);
	}
	else if(split[0] === "E4_Ibi")
	{
		currentIBI = parseFloat(split[2]);
		csvHRStream.write({HR_Timestamp: ("="+split[1]+"-"+initTime),HR:currentHR, IBI:split[2], HRV: "=ABS("+split[2]+"-"+previousIBI+")"});
		
		if(inCombat)
		{
			PhysTuple = new Array(4);
		
			PhysTuple[0] = -1;
			PhysTuple[1] = currentHR;
			PhysTuple[2] = currentIBI;
			PhysTuple[3] = previousIBI > 0 ? Math.abs(currentIBI-previousIBI) : -1;
			PhysArray.push(PhysTuple);
		}
		
		previousIBI=currentIBI;
	}	
});
setTimeout(function() {
    dev1.subscribe(EmpaticaE4.E4_IBI);
	dev1.subscribe(EmpaticaE4.E4_GSR);

}, 1000);


var net = require('net');

var server = net.createServer(function(socket) {
	socket.write('Echo server\r\n');
	socket.pipe(socket);
	
	socket.on('data', function(data)
	{
		console.log(PhysArray.length);
		if(data == "combat")
		{
			inCombat = false;
			var string = "";
			PhysArray.forEach(function(entry)
			{
				for(var i = 0; i < 5;i++)
				{
					string+=entry[i];
					string+=";";
				}
				string+=":";
				
			});
			PhysArray = [];
			socket.write(string);
			
			
		}
	});
});


server.listen(1337, '127.0.0.1');



/*
And connect with a tcp client from the command line using netcat, the *nix 
utility for reading and writing across tcp/udp network connections.  I've only 
used it for debugging myself.
$ netcat 127.0.0.1 1337
You should see:
> Echo server
*/

/* Or use this example tcp client written in node.js.  (Originated with 
example code from 
http://www.hacksparrow.com/tcp-socket-programming-in-node-js.html.) */

var net = require('net');

var client = new net.Socket();
client.connect(1337, '127.0.0.1', function() {
	console.log('Connected');
});

client.on('data', function(data) {
	console.log('Received: ' + data); // kill client after server's response
});

client.on('close', function() {
	console.log('Connection closed');
});

setTimeout(function() 
{
	client.write("combat");
},10000);