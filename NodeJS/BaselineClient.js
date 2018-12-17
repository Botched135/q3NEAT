const fs = require('fs');
const csv = require('fast-csv');
const EmpaticaE4 = require('empatica-e4-client');
const net = require('net');
const play = require('audio-play');
const load = require('audio-loader');


var buff = '';
var player = '';
var args = process.argv.slice(2);

// Setting up variables for the two connections
const ipAddress = args[0];
const portNumber = parseInt(args[1]);
const participantID = args[2];
const deviceID    = '5F04BC';  

//Generate name for csv-file --> REMEMBER TO WRITE 0 
const csvEDA5 = "CSV/Participant"+participantID+"EDABaseline5.csv";
const csvBVP5 = "CSV/Participant"+participantID+"BVPBaseline5.csv";

const csvEDA = "CSV/Participant"+participantID+"EDABaseline.csv";
const csvBVP = "CSV/Participant"+participantID+"BVPBaseline.csv";

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

var csvEDA5Stream = csv.format({headers: true,delimiter: ';'}),
    writableEDA5Stream = fs.createWriteStream(csvEDA5);
writableEDA5Stream.on("finish", function(){
  console.log("Wrote to "+csvEDA5);
});
csvEDA5Stream.pipe(writableEDA5Stream);

var csvBVP5Stream = csv.format({headers: true,delimiter: ';'}),
    writableBVP5Stream = fs.createWriteStream(csvBVP5);
writableBVP5Stream.on("finish", function(){
  console.log("Wrote to "+csvBVP5);
});
csvBVP5Stream.pipe(writableBVP5Stream);


// Variables for the physiological inputs
var dev1 = new EmpaticaE4();

var BVP_Miniute_Array = [];
var BVP_Array = [];
var BVP_Tuple = ''

var EDA_Minute_Array = []
var EDA_Array =[];
var EDA_Tuple = '';

var initTime = 0;
var currentTime = 0;
var currentValue= 0;
var sensorData = '';
var activeRecording = false;

function WriteToCSV(bvp,eda,minute_BVP,minute_EDA)
{
	bvp.forEach(function(entry)
	{
		csvBVP5Stream.write({BVP_Timestamp: entry[0], BVP: entry[1]})
	});
	csvBVP5Stream.end()

	eda.forEach(function(entry)
	{
		csvEDA5Stream.write({EDA_Timestamp: entry[0],EDA: entry[1]});
	});
	csvEDA5Stream.end()

	minute_BVP.forEach(function(entry)
	{
		csvBVPStream.write({BVP_Timestamp: entry[0], BVP: entry[1]})
	});
	csvBVPStream.end()

	minute_EDA.forEach(function(entry)
	{
		csvEDAStream.write({EDA_Timestamp: entry[0], EDA: entry[1]})
	});
	csvEDAStream.end()
}

load('./Music/MorningWalk.mp3',(err,buff) => {
	player = play(buff,
	{
		start: 0.0,
		end: buff.duration,
		volume: 1.0,
		loop: false,
		autoplay: false

	}, ()=>{
		WriteToCSV(BVP_Array,EDA_Array,BVP_Miniute_Array,EDA_Minute_Array);
	})
});

dev1.connect(portNumber ,ipAddress, deviceID, function(data){  
    sensorData = EmpaticaE4.getString(data);

	if(sensorData[0] === 'R')
	{
		console.log(sensorData)
		return;
	}

	if(!activeRecording)
	{
		player.play();
		activeRecording = true;
	}
	var dataTuple = sensorData.split("\r\n")
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
			if(player.currentTime >=240)
			{
				BVP_Miniute_Array.push(BVP_Tuple)
			}
		}
		else if(dataPoint[0] === "E4_Gsr")
		{		

			EDA_Tuple = new Array(2);
			EDA_Tuple[0] = currentTime;
			EDA_Tuple[1] = currentValue;
			EDA_Array.push(EDA_Tuple);
			if(player.currentTime >=239)
			{
				EDA_Minute_Array.push(EDA_Tuple)
			}
		}
		
	});
});
setTimeout(function() {
	dev1.subscribe(EmpaticaE4.E4_GSR);
    dev1.subscribe(EmpaticaE4.E4_BVP);
    initTime = Date.now()/1000
}, 5000);

