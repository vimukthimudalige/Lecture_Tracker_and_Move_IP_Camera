const onvif = require('node-onvif');
var sourceFile = require('./config.js');

// Create an OnvifDevice object
let device = new onvif.OnvifDevice({
  xaddr: sourceFile.xaddr,
  user : sourceFile.user,
  pass : sourceFile.pass
});

let executeAll = async () => {
  await function1();
  // await function2();
};

let function1 = () => {
    // Initialize the OnvifDevice object
    device.init().then(() => {
        console.log('pre111111');
        // Move the camera
        return device.ptzMove({
            'speed': {
                x: 1.0, // Speed of pan (in the range of -1.0 to 1.0)
                y: 0.0, // Speed of tilt (in the range of -1.0 to 1.0)
                z: 0.0  // Speed of zoom (in the range of -1.0 to 1.0)
            },
            'timeout': 1 // seconds
        });
    }).then(() => {
        console.log('Turned Back to Lecturer1111111!');
        setTimeout(() => {
            device.ptzStop().then(() => {
                console.log('PTZ Movement Stopped11111!');
            }).catch((error) => {
                console.error(error);
            });
        }, 12000);
        function2();
    }).catch((error) => {
        console.error(error);
    });
};

let function2 = () => {
    console.log("Function 2");
    device.init().then(() => {
        // Move the camera
        return device.ptzMove({
            'speed': {
                x: -1.0, // Speed of pan (in the range of -1.0 to 1.0)
                y: 0.0, // Speed of tilt (in the range of -1.0 to 1.0)
                z: 0.0  // Speed of zoom (in the range of -1.0 to 1.0)
            },
            'timeout': 1 // seconds
        });
    }).then(() => {
        console.log('Turned Back to Lecturer3333333!');
        setTimeout(() => {
            device.ptzStop().then(() => {
                console.log('PTZ Movement Stopped444444444!');
            }).catch((error) => {
                console.error(error);
            });
        }, 8000);

    }).catch((error) => {
        console.error(error);
    });
};

executeAll();