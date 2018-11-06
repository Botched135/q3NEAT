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

// Variables for the physiological inputs
var dev1 = new EmpaticaE4();

var BVP_FullArray = [];
var BVP_Array = [];
var BVP_Tuple = ''

var EDA_FullArray = []
var EDA_Array =[];
var EDA_Tuple = '';

var initTime = "0";
var currentTime = 0;
var currentValue= 0;
var sensorData = '';
var activeRecording = false;

function WriteToCSV(bvp,eda)
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

load('./Music/MorningWalk.mp3',(err,buff) => {
	player = play(buff,
	{
		start: 1.0,
		end: buff.duration,
		volume: 1.0,
		loop: false,
		autoplay: false

	}, ()=>{
		WriteToCSV(BVP_Array,EDA_Array);
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
	var replace = sensorData.replace("\r\n"," ");
	
	replace = replace.replace(',','.');
	var split = replace.split(" ");

	if(initTime === "0")
		initTime= parseFloat(split[1]);
	
	currentTime = parseFloat(split[1])-initTime;
	currentValue = parseFloat(split[2].replace(',','.')).toPrecision(8);

	if(split[0] === "E4_Bvp")
	{
		BVP_Tuple = new Array(2);
		BVP_Tuple[0] = currentTime;
		BVP_Tuple[1] = currentValue;
		BVP_Array.push(BVP_Tuple);

	}
	else if(split[0] === "E4_Gsr")
	{		
		EDA_Tuple = new Array(2);
		EDA_Tuple[0] = currentTime;
		EDA_Tuple[1] = currentValue;
		EDA_Array.push(EDA_Tuple);

	}	
});
setTimeout(function() {
    dev1.subscribe(EmpaticaE4.E4_BVP);
	dev1.subscribe(EmpaticaE4.E4_GSR);
	
}, 10000);




// Make the audio player play Morning Walk