
var w_id;
var w_callback;
var w_cnt;

function WaitLoop()
{
//  w_cnt++;
//  if (w_cnt > 2e7)
//    return;
  obj = document.getElementById(w_id);
  if (obj != undefined)
    w_callback();
  else
    setTimeout("WaitLoop()", 1);
}

function WaitForLoaded(id, callback)
{
  w_id = id;
  w_callback = callback;
  w_cnt = 0; 
  setTimeout("WaitLoop()", 1);
}
