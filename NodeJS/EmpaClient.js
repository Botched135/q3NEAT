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
const affective = args[3]
const deviceID    = '5F04BC';  

//Generate name for csv-file --> REMEMBER TO WRITE 0 
const csvEDA = "CSV/Participant"+participantID+"EDARegTest.csv";
const csvBVP = "CSV/Participant"+participantID+"BVPRegTest.csv";
const csvEDAAffect = "CSV/Participant"+participantID+"EDAAffectTest.csv";
const csvBVPAffect = "CSV/Participant"+participantID+"BVPAffectTest.csv";

if(affective == 'false')
{
// Create the two CSV streams
var csvEDAStream = csv.format({headers: true,delimiter: ';'}),
    writableEDAStream = fs.createWriteStream(csvEDA);
writableEDAStream.on("finish", function(){
  console.log("Wrote to "+csvEDA);
});
csvEDAStream.pipe(writableEDAStream);

var csvBVPStream = csv.format({headers: true,delimiter: ';'}),
    writableBVPStream = fs.createWriteStream(csvBVP);
writableBVPStream.on("finish", function(){
  console.log("Wrote to "+csvBVP);
});
csvBVPStream.pipe(writableBVPStream);
}
else
{
var csvEDAAffectStream = csv.format({headers: true,delimiter: ';'}),
    writableEDAAffectStream = fs.createWriteStream(csvEDAAffect);
writableEDAAffectStream.on("finish", function(){
  console.log("Wrote to "+csvEDAAffect);
});
csvEDAAffectStream.pipe(writableEDAAffectStream);

var csvBVPAffectStream = csv.format({headers: true,delimiter: ';'}),
    writableBVPAffectStream = fs.createWriteStream(csvBVPAffect);
writableBVPAffectStream.on("finish", function(){
  console.log("Wrote to "+csvBVPAffect);
});
csvBVPAffectStream.pipe(writableBVPAffectStream);
// Variables for the physiological inputs
}
var dev1 = new EmpaticaE4();

var BVP_FullArray = [];
var BVP_Array = [];
var BVP_Tuple = ''

var EDA_FullArray = []
var EDA_Array =[];
var EDA_Tuple = '';

var activeRecording = false;
var initTime = "0";
var currentTime = 0;
var currentValue= 0;
var sensorData = '';

function WriteToCSV(bvp,eda)
{
	if(affective == 'false')
	{
		bvp.forEach(function(entry)
		{
			csvBVPStream.write({BVP_Timestamp: entry[0], BVP: entry[1]})
		});
		csvBVPStream.end()

		eda.forEach(function(entry)
		{
			csvEDAStream.write({EDA_Timestamp: entry[0],EDA: entry[1]});
		});
		csvEDAStream.end()
	}
	else
	{
		bvp.forEach(function(entry)
		{
			csvBVPAffectStream.write({BVP_Timestamp: entry[0], BVP: entry[1]})
		});
		csvBVPAffectStream.end()

		eda.forEach(function(entry)
		{
			csvEDAAffectStream.write({EDA_Timestamp: entry[0],EDA: entry[1]});
		});
		csvEDAAffectStream.end()
	}
}

dev1.connect(portNumber ,ipAddress, deviceID, function(data)
{  
    sensorData = EmpaticaE4.getString(data);
	if(sensorData[0] === 'R')
	{

	    console.log(sensorData)
	    if(sensorData[2] === 'c')
	    {
	    	WriteToCSV(BVP_FullArray,EDA_FullArray)
        	activeRecording = false;
	    }

		return;
	}
	
	if(!activeRecording)
		return;

	var dataTuple = sensorData.split("\r\n")
	console.log(dataTuple)
	dataTuple.forEach(function(element)
	{
		var dataPoint = element.split(" ")
		try{
		currentTime = (parseFloat(dataPoint[1])-initTime).toPrecision(10)
		currentValue = parseFloat(dataPoint[2].replace(',','.')).toPrecision(10)
		}
		catch(err)
		{	
			console.log(dataTuple)
			console.log(dataPoint)
			return
		}
		if(dataPoint[0] === "E4_Bvp")
		{
			BVP_Tuple = new Array(2);
			BVP_Tuple[0] = currentTime;
			BVP_Tuple[1] = currentValue;
			BVP_Array.push(BVP_Tuple);
		}
		else if(dataPoint[0] === "E4_Gsr")
		{		

			EDA_Tuple = new Array(2);
			EDA_Tuple[0] = currentTime;
			EDA_Tuple[1] = currentValue;
			EDA_Array.push(EDA_Tuple);
		}
	});
});

setTimeout(function() {
    dev1.subscribe(EmpaticaE4.E4_BVP);
	dev1.subscribe(EmpaticaE4.E4_GSR);
}, 2500);

//UNIX SOCKET CONNECTION

//Callback for Socket

const handler = (socket) =>
{
    socket.on('data',(bytes) =>
    {
        const msg = bytes.toString();

        console.log(msg)
        if(msg == "Q3Connected")
        {
        	activeRecording = true;
        	BVP_Array = []
        	EDA_Array = [] 
        	EDA_FullArray = []
        	BVP_FullArray = []
        }
        else if(msg == "eval")
        {
        	var dataTransmission = "";
			BVP_Array.forEach(function(entry)
			{
				dataTransmission+=entry[1];
				dataTransmission+=";";
				BVP_FullArray.push(entry)	
			});
			dataTransmission+= ":";

			EDA_Array.forEach(function(entry)
			{
				dataTransmission+=entry[1];
				dataTransmission+=";";	
				EDA_FullArray.push(entry)
			});
			BVP_Array = [];
			EDA_Array = [];	
			socket.write(dataTransmission);
        }
        else if(msg == "nonAffect")
        {
         	WriteToCSV(BVP_Array,EDA_Array)
        	activeRecording = false;
        	BVP_Array = []
        	EDA_Array = [] 
        	EDA_FullArray = []
        	BVP_FullArray = []
        }
        else if(msg == "end")
        {
        	WriteToCSV(BVP_FullArray,EDA_FullArray)
        	activeRecording = false;
        	BVP_Array = []
        	EDA_Array = [] 
        	EDA_FullArray = []
        	BVP_FullArray = []
        }
    });
};

fs.unlink(
    socketPath,
    // Create the server, give it our callback handler and listen at the path
  () => net.createServer(handler).listen(socketPath)
);
