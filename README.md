UDP server that controls Robie Jr.'s motor movements

Build blog: http://robierover.blogspot.ca/

Check out youtube to see the result: https://www.youtube.com/watch?v=n8XbiNYP1GA

So how does this code work? Well basically we open up a UDP server on port 5005 and listen for commands. The data packets are 3 bytes long. Byte 0 is a "check" bit. We ensure that it is set to 1 before looking at the speed values. Byte 1 is the left wheel speed. So if byte one is positive, we tell the left wheel to go forwards (I.e. turn Robie right). We also turn the right eye green. And if it's negative we go backwards and turn the right eye red. If it's zero we turn the motor off and only display a blue light.
