CREATE TABLE domain(fqdn text not null primary key, 
					added_date timestamp not null, 
					last_change timestamp, 
					comment text, 
					top_level_domain text, 
					second_level_domain text
					);


CREATE TABLE category(id int primary key not null);

CREATE TABLE domain_query(	fqdn text not null ,
							query_time timestamp not null, 
							scoring_value int not null, 
							comment text, 
							category int not null,
							primary key (query_time, fqdn),
							FOREIGN KEY (fqdn) REFERENCES domain(fqdn),
							FOREIGN KEY	(category) REFERENCES category(id),
							UNIQUE(fqdn),
							UNIQUE(query_time)
							);
							
CREATE TABLE ns_record(id bigserial primary key not null, 
						ns inet, 
						ttl int,
						fqdn text not null,
						query_time timestamp not null,
						FOREIGN KEY (fqdn) REFERENCES domain_query(fqdn),
						FOREIGN KEY (query_time) REFERENCES domain_query(query_time));

CREATE TABLE aaaa_record(id bigserial primary key not null,
						ip_adress cidr, 
						ttl int,
						fqdn text not null,
						query_time timestamp not null,
						FOREIGN KEY (fqdn) REFERENCES domain_query(fqdn),
						FOREIGN KEY (query_time) REFERENCES domain_query(query_time));

CREATE TABLE a_record(id bigserial primary key not null,
						ip_adress cidr,
						ttl int,
						fqdn text not null,
						query_time timestamp not null,
						FOREIGN KEY (fqdn) REFERENCES domain_query(fqdn),
						FOREIGN KEY (query_time) REFERENCES domain_query(query_time));

CREATE TABLE mx_record(id bigserial primary key not null,
						preference int,
						host_name text,
						ttl int,
						fqdn text not null,
						query_time timestamp not null,
						FOREIGN KEY (fqdn) REFERENCES domain_query(fqdn),
						FOREIGN KEY (query_time) REFERENCES domain_query(query_time));
						
CREATE TABLE text_record(id bigserial primary key not null,
						text text,
						ttl int,
						fqdn text not null,
						query_time timestamp not null,
						FOREIGN KEY (fqdn) REFERENCES domain_query(fqdn),
						FOREIGN KEY (query_time) REFERENCES domain_query(query_time));


CREATE TABLE ipv4_whois_query(query_time timestamp not null,
							ipv4_adress inet not null, 
							phone text, 
							person text,
							organisation text, 
							cidr_subnet text,
							id_a_record int not null,
							PRIMARY KEY(query_time, ipv4_adress),
							FOREIGN KEY (id_a_record) REFERENCES a_record(id)
							);
							
CREATE TABLE ipv6_whois_query(query_time timestamp not null,
							ipv6_adress inet not null, 
							phone text, 
							person text,
							organisation text, 
							cidr_subnet text,
							id_aaaa_record int not null,
							PRIMARY KEY(query_time, ipv6_adress),
							FOREIGN KEY (id_aaaa_record) REFERENCES aaaa_record(id)
							);