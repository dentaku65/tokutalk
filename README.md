# tokutalk (◕‿◕ )
## Tokutalk a Pwnagotchi plugin
Switch between English and Japanese language every 10 minutes  
  
Install needed fonts  
`sudo apt update`  
`sudo apt install fonts-ipafont-gothic`
  
Place tokutalk.py in  
`/usr/local/share/pwnagotchi/custom-plugins/`  
  
Add this line in config.toml  
`main.plugins.tokutalk.enabled = true`  
  
Restart pwnagotchi  
`sudo systemctl restart pwnagotchi.service`  
  
You can enable/disable the plugin via pwnagotchi plugin web panel  
