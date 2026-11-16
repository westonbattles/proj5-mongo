Author: Weston Battles

Contact: wbattles@uoregon.edu

#### Running tests
***
Running the executable in `./DockerMongo/tests/tests.sh` performs 4 unit tests using Flask's test client (testing submissions to a temporary MongoDB database which gets deleted afterwards)<br><br>
\- btw it uses test POST submissions to /new (which is what the submit button does), and then verifies them using GET requests to /display (what the display button does)
<br>
<br>


#### Brevet Time Control Specification
***
*Calculates opening/closing times for control points in brevets of exclusively 200, 300, 400, 600 and 1000 kilometers*


<u>*Input Specification:*</u> <br>
\- Each successful submission saves a unique brevet containing all of its controls<br>
\- Control distances can contain decimals, but must be nonnegative<br>
\- Location names are optional<br>
\- Blank control rows are skipped<br>
\- One control is required for submission<br>
\- Total brevet distance must be 200, 300, 400, 600 or 1000km <br>

<br>



<u>*Calculation Rules:*</u> <br>
Opening times are calculated using maximum speeds for given distance intervals and closing times are calculated using minimum speeds (as given by the following): <br>

(*intervals are lower-exclusive and upper-inclusive*)<br>
0-200km: 15km/h min speed, 34km/h max speed<br>
200-400km: 15km/h min speed, 32km/h max speed<br>
400-600km: 15km/h min speed, 30km/h max speed<br>
600-1000km: 11.428km/h min speed, 28km/h max speed<br>
1000-1300km: 13.333km/h min speed, 26km/h max speed<br>

For controls spanning multiple of these distance intervals, the time for each interval is simply calculated separately and summed. The resulting elapsed time is rounded to the nearest minute and added to the actual brevet start time.

<u>__*SPECIAL CASES!:*__</u><br>
\- Controls at 0km start at the brevet start time, and close exactly one hour later <br>
\- The maximum closing time for controls are as follows:<br>
&emsp;&emsp;&emsp;FOR 200KM BREVETS: 13h30m<br>
&emsp;&emsp;&emsp;FOR 300KM BREVETS: 20h<br>
&emsp;&emsp;&emsp;FOR 400KM BREVETS: 27h<br>
&emsp;&emsp;&emsp;FOR 600KM BREVETS: 40h<br>
&emsp;&emsp;&emsp;FOR 1000KM BREVETS: 75h<br>
\- Control distances that are beyond the brevet distance are capped to that brevet distance for time calculations<br>
\- For controls within the first 60 km, closing times are calculated using a minimum speed of 20 km/h, plus one additional hour. For controls at and beyond 60 km, the standard minimum-speed calculation applies