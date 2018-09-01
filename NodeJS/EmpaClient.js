const fs = require('fs');
const csv = require('fast-csv');
const EmpaticaE4 = require('empatica-e4-client');
const net = require('net');

var args = process.argv.slice(2);

// Setting up variables for the two connections
const socketPath = '/tmp/AffectSocket';
const ipAddress = args[0];
const portNumber = parseInt(args[1]);
const participantID = args[2];
const deviceID    = '5F04BC';  

//Generate name for csv-file --> REMEMBER TO WRITE 0 
const csvEDA = "CSV/Participant"+participantID+"EDA.csv";
const csvHR = "CSV/Participant"+participantID+"HR.csv";

// Create the two CSV streams
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


// Variables for the physiological inputs
var dev1 = new EmpaticaE4();

var PhysArray =[];
var PhysTuple = '';

var inCombat = false;
var initTime = "0";
var sensorData = '';
var currentHR = -1;
var currentHRV = -1;
var currentEDA = -1;
var currentIBI = -1;
var previousIBI = 0;


dev1.connect(portNumber ,ipAddress, deviceID, function(data){  
    sensorData = EmpaticaE4.getString(data);
	if(sensorData[0] === 'R')
	{
		console.log(sensorData)
		return;
	}
	
	var replace = sensorData.replace("\r\n"," ");
	
	replace = replace.replace(',','.');
	var split = replace.split(" ");

	if(initTime === "0")
		initTime= parseFloat(split[1]);
	
	if(split[0] === "E4_Gsr")
	{		
		currentEDA = parseFloat(split[2].replace(',','.')).toPrecision(8);
		csvEDAStream.write({EDA_Timestamp: (parseFloat(split[1])-initTime),EDA: currentEDA.toPrecision(8)});
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
		currentHR = parseFloat(split[2].replace(',','.')).toPrecision(8);
	}
	else if(split[0] === "E4_Ibi")
	{
		currentIBI = parseFloat(split[2].replace(',','.')).toPrecision(8);
		currentHRV = previousIBI > 0 ? Math.abs(currentIBI-previousIBI) : -1;
		csvHRStream.write({HR_Timestamp: (parseFloat(split[1])-initTime),HR:currentHR, IBI:currentIBI, HRV: currentHRV});
		
		if(inCombat)
		{
			PhysTuple = new Array(4);
		
			PhysTuple[0] = -1;
			PhysTuple[1] = currentHR;
			PhysTuple[2] = currentIBI;
			PhysTuple[3] = currentHRV
			PhysArray.push(PhysTuple);
		}
		
		previousIBI=currentIBI;
	}	
});
setTimeout(function() {
    dev1.subscribe(EmpaticaE4.E4_IBI);
	dev1.subscribe(EmpaticaE4.E4_GSR);

}, 1000);


//UNIX SOCKET CONNECTION

//Callback for Socket

const handler = (socket) =>
{
    socket.on('data',(bytes) =>
    {
        const msg = bytes.toString();

        console.log(msg)
        if(msg == "combat")
        {
        	inCombat = true;
        }
        else if(msg == "end")
        {
        	inCombat = false;
        }
        else if(msg == "eval")
        {
        	var dataTransmission = "";
			PhysArray.forEach(function(entry)
			{
				for(var i = 0; i < 4;i++)
				{
					dataTransmission+=entry[i];
					dataTransmission+=";";
				}
				dataTransmission+=":";
				
			});
			console.log(PhysArray.length);
			PhysArray = [];
			socket.write(dataTransmission);
			inCombat = false;
        }
    });
};

fs.unlink(
    socketPath,
    // Create the server, give it our callback handler and listen at the path
  () => net.createServer(handler).listen(socketPath)
);