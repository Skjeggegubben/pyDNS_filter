# pyDNS_filter

This is a tiny DNS server script written in python 3. In home wifi router settings you usually have the possibility to set a custom DNS server to be used in stead of the one built-in on the router, and all devices that connect to the router on wifi usually haven't specified a DNS server to <b>always</b> use, so they will by default be set to use the DNS server that is provided to them by the wifi router upon connect. This means that, you can set a small device like a little raspberry pi, to actually function as a home network DNS server for monitoring and filtering, you just set the IP for the device that is running the DNS server in your router config and it should work. 

The script is straight forward and should be easy to read and understand. It listens for packets on DNS standard UDP port 53. It extracts what domain is requested from the data in the packet, and either passes the request through or makes a custom reply packet with IP reply according to rewrite rules set in a custom hosts file. If the domain is not in the rewrite list, the DNS request from client just gets forwarded to google's DNS and the reply is in turn forwarded back to the client who was requesting, who wont know the difference. If in the list, the DNS lookup reply will contain the IP address you've set it to reply, and the client device will try to connect to that IP instead of the actual real IP of the requested domain. 

This can be helpful on a home network for filtering out unwanted domains, to stop your kids or loved ones from going on this or that site, send the kids to their school homework page when they try to open youtube etc, you'll basically be able to monitor in realtime what domains they are using but ofc not the entire URL or any of the data. Would be possible to add a few lines to customize particular times of day the rewrite rules should apply, or to add for what IP in your network they should or shouldn't apply.

If you set it to reply just some IP that isn't hosting anything, the client browser will show its standard "unable to connect" message, possibly making the user believe that instagram e.g. is just "down" for the moment and will be none the wiser. If you set it to reply an IP address where you actually do host a HTTP server capable of serving for real, you can make it so that if your kid or hubby is trying to open instagram to look at chicks after 21:00, he gets to see a nice pic of his granny in bikini in her younger days, with a big text saying "GO TO BED" e.g. Lots of fun possibilities! 

This could also be developed into the type of systems you see at shops, shopping malls or hotels, where you'd be restricted to only browse their customer service or shop webpage if you don't register / log in with e-mail / pay up in order to get unrestricted web access when on their wifi. Imagine forcing your neighbour to pay up for piggy-backing on your wifi :D My code is not perfect, but it shows the idea, and although I don't care about handling every header byte and their values etc, this method does extract domain just fine from the packets, and the tampered response packets with IP are formatted as should. For a big network I expect it to fail, wont be quick enough to handle a ton of packets at once, but should suffice for a bit of filtering at home!

Run it in terminal by typing:

sudo python pyDNS_filter_run.py

And yes, sudo is needed because of port restrictions in linux.
Supports only IPv4 sadly, haven't added special support for IPv6 in reply packets.

This server is reloadable, meaning you can edit the source code file or the hosts file in runtime and just hit ctr-c and enter at any time to reload. 
