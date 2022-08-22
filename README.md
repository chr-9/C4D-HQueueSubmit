# C4D-HQueueSubmit
Script to submit jobs from Cinema4D to HQueue.  

## Usage
1. Place hqueue_submit.py under <Maxon Cinema 4D R**\library>.
1. Change the paths in c4d.bat to match your environment.
1. Place c4d.bat under the C: of the rendering machine (or the location specified in client_c4dloc).
  
All assets must be in a shared location on the network, such as a NAS.  
For Maxon licensing purposes, the HQueueClient service must run under the user's account.

## Todo
Submitting a job with multiple frames grouped together (to reduce overhead at C4D startup)
