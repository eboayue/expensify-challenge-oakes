# Design
Given the prompt, there is not much to do with the design other than choose specific tools for each task. That said, I do want to use a config management tool even though it's not specified. It's more upfront work but it'll be much easier to keep track of what I'm doing that way. Would love to use Terraform, but I suspect it's more work than it's worth to try and set it up without a cloud provider. So we'll use Ansible, and stick the playbook on github.

Nginx seems like the obvious, simple choice for serving just one web page, and there is an Ansible plugin for it. I considered also using it to load balance, but when I searched around it seems I would not be able to get the sticky functionality I need with just the open source version. So instead I'll use HAProxy, which has good config options that should work for what I want.

## Server Roles:

### Nagios/Ansible (35.95.66.224)
This is the primary server - It is the only server server accessible via SSH from outside, and runs services that affect the all of the other servers.

Services:
- Nagios - Runs basic monitoring and alerting on subordinate hosts and itself. Serves results to a dashboard accessible from a browser (using Apache)
- Ansible - Manages the configuration of itself and subordinate hosts. Will adjust settings for any specified services if necessary, when it is run
- UFW - Allows external ssh access and ssh to the other servers, making this the jumphost. Allows Nagios and Ansible to communicate to the other hosts.

### Load Balancer (54.202.28.125)
- HAProxy - Load balancing tool that ingests traffic on the specified ports and serves it to the webservers. Also serves stats about itself to a dashboard accessible from a browser
- UFW - Allows ssh from the jumphost, and http to/from specified ports

### Webservers (54.191.190.151/34.221.22.164)
- Nginx - Serves a webpage to the specified port
- UFW - Allows ssh from the jumphost, and http to/from specified ports

## If wanted to do more:
If I had more time or servers, or was setting this up more permanently, I would write a bash setup script to automate adding an ansible user and ssh key to subordinate hosts. I would also set up ansible to run changes on a schedule rather than ad-hoc

# Challenges
- I tried to set up Puppet at first, since I was already familiar with it. The thing is, I was familiar wth using already-set-up Puppet; I was very much not familiar with going through the tedium of setting it up myself. It really didn't help that the Puppet docs now constantly redirect to pages that go nowhere, seemingly in an effort to get you to pay for a service. I was not a fan of the open source unfriendliness, and when my designated Puppet server suddenly became unreachable and Phillip had to reprovision it, I decided to explore other options. Ansible came out the clear winner because of the great documentation - I had it up and running in no time despite never having used it before. There was a small learning curve, but it was fun to learn a new tool :)
- If I did this again I wouldn't bother making an ansible user - it's best practice for a long term situation but here it just complicated running the software for not much gain
- Speaking of the Ansible user, one thing did trip me up for a while when I was figuring out how to use it. I gave the user sudo permissions, thinking that when it ran the playbooks that would be enough to allow it to do what it needed to do. But I didn't think about the fact that just having sudo doesn't mean a user is running as root all the time - I needed to specifiy in the playbook that it actually needed to use sudo to become root to do things like adding a user.
- I needed to set up a htdigest.users file to configure Apache for Nagios, but that's sensitive info and I was committing this all to github. I could use Ansible vault to encrypt the info, but then It would need a password. The Ansible docs recommend saving that password in something like Secrets Manager so you can use it automatically - I probably could have made that work, but it didn't seem worth the effort. So I just encrypted with ansible-vault, and entered the password when running the playbook
- The Nagios docs are... not great? To put it diplomatically? I really struggled to figure out how to install and configure all the different things for Nagios (this is another tool I've only ever used, not set up). The docs don't do a great job of illustrating differences between distros, telling you where files are, or explaining how the config files work. Sometimes the information was inaccurate, which led to more issues on my part. I took bits from probably 8 different user-created setup guides to eventually get to the working configuration I have now.
- At some point I asked chatgpt some questions to confirm I had the right idea, design-wise. It gave me beautifully detailed and also woefully insufficient answers to my questions. It had the same general idea, but when it did give me actual instructions, they were usually outright wrong or missing something. I did find it useful as a kind of rubber-duck for some things though, particularly when I was trying to get the HAProxy configuration down and I wanted to be sure I had read the documentation correctly.

# Important info
[Nagios dashboard](http://35.95.66.224/nagios4/)
[HAProxy dashboard](http://54.202.28.125:8404/stats#webservers/) - username and password given to Phillip
Ansible can only be run from the ansible user, and needs a password to decrypt a sensitive file. The password has been given to Phillip

### Sources:
[Nagios docs](https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/toc.html)
[Ansible docs](https://docs.ansible.com/)
[HAProxy docs](https://www.haproxy.com/documentation/haproxy-configuration-manual/latest/)
[DigitalOcean UFW cheatsheet](https://www.digitalocean.com/community/tutorials/ufw-essentials-common-firewall-rules-and-commands)
[Apache docs](https://httpd.apache.org/docs/)
