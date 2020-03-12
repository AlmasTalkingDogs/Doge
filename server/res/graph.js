var datalist = {};
var currentGraph = 0;

//function that takes in divID and websocket as well as configs
//meant to correlate the data sent in from websocket
function plot(divId, websocket, configs) {
  var counter = 0;

  for(i in configs) {
    datalist[configs[i]] = [];
  }
  var layout = {
    title: 'EEG Livestream',
    xaxis: {
      fixedrange: true,
      showticklabels: false
    },
    yaxis: {
      fixedrange: true
    },
    trace2: {
      visible: false
    }
  };
  let dataset = [];
  for(key in datalist) {
    dataset.push({
      y: datalist[key],
      type: 'scatter'
    })
  }
  Plotly.plot(divId, dataset, layout, {displayModeBar: false});
  // setInterval(function(){
  //   let index = 0;
  //   for(key in datalist) {
  //     newdata = getData(key);
  //     console.log(newdata)
  //     if(newdata != '0' && key !== "flag") {
  //       Plotly.extendTraces(divId, {y: [[newdata]]}, [index]);
  //     }
  //     index++;
  //     counter++;
  //     }
  // },60);

  // Do we assume that the configs always mach the number of data in the message?

  websocket.onmessage = function(msg) {
    // console.log(msg)
    msg_data = msg.data.split(",");
    for(index in msg_data) {
      if (parseInt(index) >= configs.length) {
        break;
      }
      datalist[configs[index]].push(parseInt(msg_data[index]));
      // console.log(data, index);

    }
    for(index in configs) {
      if(datalist[configs[index]].length >= 50) {
        if(parseInt(index) < 2) {
          Plotly.extendTraces(divId, {y: [datalist[configs[index]]]}, [parseInt(index)], 500);
        }
        datalist[configs[index]] = [];
      }
    }
  }
}

// feedSocket.onopen = function() {
//     console.log("onopen")
// }

// feedSocket.onclose = function() {
//     console.log("onclose")
// }
