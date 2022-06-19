import dns.resolver

# exceptions fangen! Wichtig!

#####################################
#answers = dns.resolver.query('w-hs.de') #perference / exchange
#answers = dns.resolver.resolve('w-hs.de', 'NS') # target
answers = dns.resolver.query('w-hs.de', 'A') # address / to_text
#answers = dns.resolver.query('w-hs.de', 'AAAA') # address / to_text
#answers = dns.resolver.query('w-hs.de', 'TXT') # strings


for rdata in answers:
    print('Host', rdata.address,'address' ,rdata.to_text,'TTL',answers.rrset.ttl)