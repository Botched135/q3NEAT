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
const csvBVP = "CSV/Participant"+participantID+"BVP.csv";

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

var inCombat = false;
var initTime = "0";
var currentTime = 0;
var currentValue= 0;
var sensorData = '';

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
		//csvEDAStream.write({EDA_Timestamp: (parseFloat(split[1])-initTime),EDA: currentEDA.toPrecision(8)});
		EDA_Tuple = new Array(2);
		EDA_Tuple[0] = currentTime;
		EDA_Tuple[1] = currentValue;
		EDA_Array.push(EDA_Tuple);

	}	
	/*else if(split[0] === "E4_Hr")
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
	}	*/
});
setTimeout(function() {
    dev1.subscribe(EmpaticaE4.E4_BVP);
	dev1.subscribe(EmpaticaE4.E4_GSR);
}, 1000);

setTimeout(function()
{
	WriteToCSV(BVP_Array,EDA_Array);
},10000)

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
			EDA_Tuple = [];
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