endpoint = {}
endpoint['url'] = "https://mylesdomain.com:443/blog/posts"
domain = endpoint["url"].split("//")[-1].split("/")[0]
if ':' in domain:
    domain = domain.split(':')[0]
else:
    pass

print(domain)