# Mikan-Webpage-Crawler
A self written python code to get download link from Mikan Project, proxy is an option since it's somehow unreachable for me. BTW you can always find yourself a free or paid proxy list if you can access Github, so forgive me for not bringing extra traffic to the proxy pool I use.

The code was compiled in 3.11 while it still works for 3.8 on my Windows7 laptop. The GUI is quite clear -- well for me anyway.
![image](https://user-images.githubusercontent.com/14989953/236103831-91a46720-e48a-4574-b53e-663bd538be8c.png)

This code crawls magnet and torrent link from list page, search page and bangumi page. It also works for detailed page while I found it not very effecient -- after all, it requires almost 20+ more connections while all these links can be accessed on the overall pages.

The proxy part isn't perfect: for people do need proxy to access Mikan, such us humble I, the thread pool would somehow stuck at some level if you have 1k more proxy on your list. I believe the issue occurs for both the thread pool gabage collection methology -- if it has any -- and the timeout resource waste when it tries every proxy using requests.get(). I believe there is a better way to do it. 

Afterall, this is not such a useful or 'good' project: people can visit Mikan Project don't need to use such a web crawler, personal speaking there is more fun to browse the page and pick what I want; on the other hand, for people can't access the website directly, a stable VPN or proxy is quite enough. This project is merely for people who can't or don't want to pay for a VPN or proxy in any form, and still want to download and watch the newly released cartoons at the same time.

Everyone is welcome to use this code or modify it as long as you find it's helpful. But DO REMEMBER, try not use it too frequently to bring too much traffic burden to Mikan Project -- it's a great website, and I don't want to ruin it for anyone.
