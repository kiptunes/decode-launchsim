# decode-launchsim
A projectile motion simulator specifically for FTC DECODE 2024.

![Screenshot of the simulator.](launchsim_preview.png)

## Troubleshooting

- Note that velocity is taken in meters per second but the distance from the goal is taken in centimeters. this is for better readability.

- If you are editing a textbox, you cannot use the arrowkeys/spacebar to move the robot---you have to click off the textbox. Just hit enter to return to the previous value.

- if requirements are broken try:
~~~
pip install pygame
pip install pygame-textinput
~~~

## About
FTC Decode this year allows for projectile shooting, which is wonderful and so much fun, except I watched the "robot in 30 hours" videos and it seemed they were having trouble shooting accurately! I thought I'd go ahead and make a Decode-specific simulator in the python library I was most familiar with, which happened to be pygame.

If I get around to cleaning up this code later on I would love to break apart that one terrible main.py file into smaller pieces, but for now at least it works, and I promise the math works out alright.

##
<br>Thank you for visiting/downloading! ^_^
<br><br>If you have other issues I would be happy to revisit this code but as you can probably tell this was my first time making a project like this one and it's so comically bad I'm not sure I'll be able to fix it without bulldozing a lot of things. Still, any bug reports are appreciated.

[![Athena Award Badge](https://img.shields.io/endpoint?url=https%3A%2F%2Faward.athena.hackclub.com%2Fapi%2Fbadge)](https://award.athena.hackclub.com?utm_source=readme)

