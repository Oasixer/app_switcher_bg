# goals
* gets some sort of app type input
* every 0.01 sec or so (or ideally when changing windows), the client side app will check:
  * whether the current window has changed or not. If it has changed, then a request is sent to the backend which says what the new top app is.
  * whether any windows have been closed since last iteration. If a window was closed, a request is sent with that update as well
* backend needs to keep these in some sort of FIFO so that when a request is made to get the most recent window PID matching some argument (ie. the first letter of the program name), it can be returned
* also keep some sort of program name mapping



* settings:
  * dont tab to small terminals
  * dont tab to terminals on monitor 2
* inputs: 
