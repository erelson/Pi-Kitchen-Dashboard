# Modifications and notes
##### Original README is after this section

I'm running this in 2020, after initially setting up in 2018, but never being fully happy with
some things at the time. After some more work, I think I'm now happy with the state of things!
It's nothing fancy, and hardly modern...

- I added event info for a nearby football stadium, so I know when traffic and parking might
be bad.  This uses the Eventful API which seems to work pretty well.  I use the API via
`get_events.py`, which generates `~/events.html`.
- I modified the index.html to include this bit dynamically, with much help from Google.
- A crontab job (i.e. `crontab -e` runs `get_events.py` and then copies `events.html` into
`~/repos/Pi-Kitchen-Dashboard/skins/default/`.
- Auto-starting at boot-up: I originally tried to use the Midori browser, but it wouldn't
seem to let jquery load HTML from another file.  But Firefox would. But I couldn't get Firefox
to run at startup....
- Now I know a bit more: I use `~/.config/autostart/pi-kitchen-dashboard.desktop` to run a bash
script `~/Desktop/launch_hmi_dashboard.bash` which (1) launches Firefox, (2) waits for Firefox
window to open, and (3) uses `xdotool` to put full-screen and put the mouse cursor off to the side.
- After updating the Firefox version in late 2020, dynamic HTML insertion stopped working. This
was fixed by disabling in Firefox's about:config, the property `privacy.file_unique_origin`.
- Also, the Yahoo Weather that the upstream project's README refers to is now replaced by using
OpenWeather. Easy enough. There's a few references to Yahoo that are still there in upstream.
- My setup is near the front door.  To make the screen auto wake, I added a PIR sensor to
pin 8, with an indicator LED on pin 10.
- Script `screen_wake_with_IR.py` monitors the PIR sensor and triggers the screen to wake up.
It also sets the screen to turn off after 2 minutes.

A laundry list of things needed in setup that are left as exercises to the user:

+ Clone this repo, e.g. to `~/repos/Pi-Kitchen_Dashboard`
+ Install `xdotool` and `wmctrl` via your package manager
+ Grab a jquery library version and match/update the reference to it in `index.html`
+ Obtain OpenWeather API key and put it in `js/weather.js`
+ Obtain Eventful API key and put it in environment variable `EVENTFUL_KEY`
+ Set up a cron job to run `events/get_events.py` and copy its output to path mentioned above
(e.g. daily at 1am)
+ Put `autostart/launch_hmi_dashboard.bash` in `~/Desktop` (might need to check paths in script)
+ Put `pi-kitchen-dashbaord.desktop` in `~/.config/autostart`
+ Create a boot-time crontab job like:
`@reboot sleep 60 && DISPLAY=:0 python3 $HOME/repos/Pi-Kitchen-Dashboard/screen_wake_with_IR.py &> $HOME/output-screen_wake_with_IR.py.log`

![Example Screenshot](/images/weather_events_dashboard.png)

# Pi Kitchen Dashboard
##### Because thrift store monitors still need things to do.

This project turns your monitor and Raspberry Pi into a simple, skinnable time and weather dashboard for your kitchen. Want it in your living room? **Too bad.**

![alt text](https://lh5.googleusercontent.com/OvyLwyLtXF69AJ-8U68OPnLXhZNwOPG7JYv5i-fa_44=w1167-h875-no "Pi Kitchen Dashboard")

* * *

+ [Items Needed](#itemsNeeded)
+ [Instructions](#instructions)
    - [Cloning](#cloning)
    - [Fulfilling requirements](#fulfillingRequirements)
    - [Setting your location](#settingYourLocation)
    - [Configuring your Pi](#configuringYourPi)
        * [Disallowing screen sleep](#disallowingScreenSleep)
        * [Installing Unclutter](#hidingCursor)
        * [Installing Midori](#installingMidori)
        * [Auto-starting Unclutter and Midori](#autoStartingMidori)
    - [Scheduling screen sleep](#scheduling)
+ [Changing the skin](#changingTheSkin)
+ [Creating skins](#creatingSkins)
+ [Credit](#credit)

* * *

## <a name="itemsNeeded"></a>Items needed

+ Raspberry Pi
+ Monitor
+ Adapter to hook said Raspberry Pi to said monitor
+ Internet connection

## <a name="instructions"></a>Instructions

### <a name="cloning"></a>Cloning

Clone this repository with `git clone https://github.com/userexec/Pi-Kitchen-Dashboard.git`.

If your Pi does not currently have git, you will need to install it first with `sudo apt-get install git`.

### <a name="fulfillingRequirements"></a>Fulfilling requirements

This project is not distributed with its dependencies; however, [Bower](http://bower.io/) will automatically pull them in.

1. `sudo apt-get update && sudo apt-get upgrade` - Update your system
2. Install Node Package Manager (required for Bower) 

  ##### Raspberry Pi A/B/B+

  ```
  wget https://nodejs.org/dist/v4.0.0/node-v4.0.0-linux-armv6l.tar.gz 
  tar -xvf node-v4.0.0-linux-armv6l.tar.gz 
  cd node-v4.0.0-linux-armv6l
  sudo cp -R * /usr/local/
  ```

  ##### Raspberry Pi 2 Model B

  ```
  wget https://nodejs.org/dist/v4.0.0/node-v4.0.0-linux-armv7l.tar.gz 
  tar -xvf node-v4.0.0-linux-armv7l.tar.gz 
  cd node-v4.0.0-linux-armv7l
  sudo cp -R * /usr/local/
  ```
  <a href="http://blog.wia.io/installing-node-js-v4-0-0-on-a-raspberry-pi/">Node install instructions</a> by <a href="http://blog.wia.io/author/conall/">Conall Laverty</a>
    

3. `sudo npm install -g bower` - Install Bower
4. `cd ~/Pi-Kitchen-Dashboard` - cd into the directory of the cloned project
5. `bower install` - Install the project's dependencies

### <a name="settingYourLocation"></a>Setting your location

Open `js/weather.js` and find the following section at the top:

```javascript
// Your Yahoo WOEID code
// Find your WOEID code at http://zourbuth.com/tools/woeid/
var woeid = 23416998;

// Your temperature unit measurement
// This bit is simple, 'c' for Celcius, and 'f' for Fahrenheit
var unit = 'c';

// Yahoo! query interval (milliseconds)
// Default is every 15 minutes. Be reasonable. Don't query Yahoo every 500ms.
var waitBetweenWeatherQueriesMS = 900000;
```

Change these variables to match your location, unit measurement, and desired update interval, and your part of the coding is done!

### <a name="configuringYourPi"></a>Configuring your Pi

You will need a Raspberry Pi (although you could use anything else) with Raspbian (again, or anything else) and an internet connection. To complete the dashboard, your Pi will need disallow screen sleep and automatically start kiosk mode.

#### <a name="disallowingScreenSleep"></a>Disallowing screen sleep

Unless screen sleep is prevented, the dashboard screen will go black after a few minutes and require a mouse movement or keypress to wake up. Scheduled times for the display to turn off are covered in a [later section](#scheduling).

`sudo nano /etc/lightdm/lightdm.conf`

Add the following lines to the [SeatDefaults] section:

```bash
xserver-command=X -s 0 -dpms
```

#### <a name="hideCursor"></a>Installing Unclutter

Unclutter causes the mouse cursor to disappear when the mouse isn't being moved. This prevents the dash from having a cursor over the middle unless you plug in a mouse and move it elsewhere.

`sudo apt-get install unclutter`

#### <a name="installingMidori"></a>Installing Midori

Midori is used for its compatibility with multiple RPi generations and reasonably solid rendering. Other browsers may be used if preferred using much the same strategy.

`sudo apt-get install midori`

#### <a name="autoStartingMidori"></a>Auto-starting Unclutter and Midori

1. Create a new directory at `~/.config/autostart` if it does not exist
2. `cd ~/.config/autostart` - cd into this directory
3. `nano unclutterAuto.desktop` - Create a new .desktop file
4. Add the following lines and save. Customize the file path to where this project's index.html lives on your Pi.

	```
	[Desktop Entry]
	Type=Application
	Exec=unclutter -idle 0.1
	```
5. `nano midoriAuto.desktop` - Create a new .desktop file

	```
	[Desktop Entry]
	Type=Application
	Exec=midori -e Fullscreen -a file:///home/pi/Pi-Kitchen-Dashboard/index.html
	```

Your Pi should now atomatically start kiosk mode and show the dashboard full screen once your desktop loads.

If your time or date are incorrect, use `sudo raspi-config` to set your locale and timezone.

### <a name="scheduling"></a>Scheduling screen sleep

If you don't want your display to run 24/7, you can use cron jobs to fire a pair of included bash scripts: screenOff.sh and screenOn.sh. Please ensure you've completed the [Disallowing screen sleep](#disallowingScreenSleep) step above in order to keep the display always on during the times it's scheduled to be on.

1. `cd` into your Pi-Kitchen-Dashboard directory and set both scripts to executable
	
	```bash
	chmod +x screenOff.sh
	chmod +x screenOn.sh
	```

2. Run `crontab -e` and add cronjobs to the end using the provided scripts. If you're not comfortable writing cronjobs manually, you can use a <a href="http://cron.nmonitoring.com/cron-generator.html">crontab generator</a>. The following lines, for example, shut off the display at 11:00PM each night and turn it back on at 6:00AM. Be sure to edit the file paths if necessary.
	
	```
	0 23 * * * /home/pi/Pi-Kitchen-Dashboard/screenOff.sh
	0 6 * * * /home/pi/Pi-Kitchen-Dashboard/screenOn.sh
	```

## <a name="changingTheSkin"></a>Changing the skin

Skins are kept, conveniently, in the skins folder. To switch skins, edit `Pi-Kitchen-Dashboard/index.html` and insert the folder name of the skin you wish to use where the comments direct.

## <a name="creatingSkins"></a>Creating skins

Creating your own skin or a new skin for distribution is easy and only requires knowledge of HTML and CSS. Just copy the `default` folder under skins, rename it, and begin editing. Comments in the default skin will guide you through the process, but it basically boils down to 99% using your imagination and 1% placing a few IDs and classes so that time and weather data can be auto-populated.

## <a name="credit"></a>Credit

Weather icons by Lukas Bischoff and Erik Flowers https://github.com/erikflowers/weather-icons. Icons licensed under [SIL OFL 1.1](http://scripts.sil.org/OFL).  

Time formatting by [Moment.js](http://momentjs.com/)  

Weather data retrieved using Yahoo! Weather API.  

Default skin responsiveness by [RYJASM](https://github.com/ryjasm).

Project is under [MIT license](http://choosealicense.com/licenses/mit/).  
