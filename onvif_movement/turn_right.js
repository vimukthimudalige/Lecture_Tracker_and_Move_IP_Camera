var HOSTNAME = '192.168.1.110',
PORT = 8999,
USERNAME = 'admin',
PASSWORD = '',
STOP_DELAY_MS = 200;

var Cam = require('./lib/onvif').Cam;

var stop_delay = process.argv[2];

if((process.argv[2] === undefined)){
    console.log("No args. command / speed");
}
else{
    //console.log('test '  + stop_delay );
    STOP_DELAY_MS = stop_delay;
}

new Cam({
	hostname : HOSTNAME,
	username : USERNAME,
	password : PASSWORD,
	port : PORT,
	timeout : 10000
}, function CamFunc(err) {
	if (err) {
		console.log(err);
		return;
	}

	var cam_obj = this;
	var stop_timer;
	var ignore_keypress = false;
	var preset_names = [];
	var preset_tokens = [];

	cam_obj.getPresets({}, // use 'default' profileToken
		// Completion callback function
		// This callback is executed once we have a list of presets
		function (err, stream, xml) {
			if (err) {
				console.log("GetPreset Error "+err);
				return;
			} else {
				// loop over the presets and populate the arrays
				// Do this for the first 9 presets
				//console.log("GetPreset Reply");
				var count = 1;
				for(var item in stream) {
					var name = item;          //key
					var token = stream[item]; //value
					// It is possible to have a preset with a blank name so generate a name
					if (name.length == 0) name='no name ('+token+')';
					preset_names.push(name);
					preset_tokens.push(token);

					// Show first 9 preset names to user
					/*if (count < 9) {
						console.log('Press key '+count+ ' for preset "' + name + '"');
					count++;
					}*/
				}
				move(1,0,0,'right');
			}
		}
	);

	//1 preset left max
	//2 preset is left normal
	//3 preset right normal
	//4 preset exactly middle
	//5 preset right max
	
	function move(x_speed, y_speed, zoom_speed, msg) {
		// Step 1 - Turn off the keyboard processing (so key-presses do not buffer up)
		// Step 2 - Clear any existing 'stop' timeouts. We will re-schedule a new 'stop' command in this function 
		// Step 3 - Send the Pan/Tilt/Zoom 'move' command.
		// Step 4 - In the callback from the PTZ 'move' command we schedule the ONVIF Stop command to be executed after a short delay and re-enable the keyboard

		// Pause keyboard processing
		ignore_keypress = true;

		// Clear any pending 'stop' commands
		if (stop_timer) clearTimeout(stop_timer);

		// Move the camera
		console.log('sending move command ' + msg);
		cam_obj.continuousMove({x : x_speed,
					y : y_speed,
					zoom : zoom_speed } ,
				// completion callback function
				function (err, stream, xml) {
					if (err) {
						console.log(err);
					} else {
						console.log('move command sent '+ msg);
						// schedule a Stop command to run in the future 
						stop_timer = setTimeout(stop,STOP_DELAY_MS);
					}
					// Resume keyboard processing
					ignore_keypress = false;
				});
		}

	function stop() {
		// send a stop command, stopping Pan/Tilt and stopping zoom
		console.log('sending stop command');
		cam_obj.stop({panTilt: true, zoom: true},
			function (err,stream, xml){
				if (err) {
					console.log(err);
				} else {
					console.log('stop command sent');
					//exit process once done!
					process.exit();
				}
			});
	}

	function goto_preset(number) {
		if (number > preset_names.length) {
			console.log ("No preset " + number);
			return;
		}

		console.log('sending goto preset command '+preset_names[number-1]);
		cam_obj.gotoPreset({ preset : preset_tokens[number-1] } ,
			// completion callback function
			function (err, stream, xml) {
				if (err) {
					console.log(err);
				} else {
					console.log('goto preset command sent ');
					//exit process once done!
					process.exit();
				}
			});
	}
});