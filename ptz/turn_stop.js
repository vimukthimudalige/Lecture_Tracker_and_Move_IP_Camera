const onvif = require('node-onvif');
var sourceFile = require('./config.js');

// Create an OnvifDevice object
let device = new onvif.OnvifDevice({
  xaddr: sourceFile.xaddr,
  user : sourceFile.user,
  pass : sourceFile.pass
});


// Initialize the OnvifDevice object
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
  //console.log('Done!');
  // Stop to the PTZ in 2 seconds  2000
  setTimeout(() => {
    device.ptzStop().then(() => {
      console.log('PTZ Movement Stopped!');
    }).catch((error) => {
      console.error(error);
    });
  }, 0);
}).catch((error) => {
  console.error(error);
});