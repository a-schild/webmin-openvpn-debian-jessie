#########################################################################
#   Autori:             Marco Colombo (marco@openit.it)
#                       Giuliano Natali Diaolin (diaolin@openit.it)
#   Copyright:          Open It S.r.l.
#                       Viale Dante, 78
#                       38057 Pergine Valsugana (TN) ITALY
#                       Tel: +39 0461 534800 Fax: +39 0461 538443
##############################################################################

# openvpn-lib.pl
# Common functions used for openvpn module

use Time::Local;

do '../web-lib.pl';

&init_config();

require '../ui-lib.pl';

# config_icons(context, program)
# Displays up to 18 icons, one for each type of configuration directive, for
# some context (global, virtual, directory or htaccess)
sub config_icons {
    local (@titles, @links, @icons, $i);
    for($i=1; $i<@_; $i++) {
	push(@links, $_[$i]->{'link'});
	push(@titles, $_[$i]->{'name'});
	push(@icons, $_[$i]->{'icon'});
    }
    &icons_table(\@links, \@titles, \@icons, 5);
    print "<p>\n";
}

# Crea la CA
sub create_CA {
    local ($info,$ok,$dir,$k,$string_export,$wadir);
    $info = $_[0];
    $dir = $$info{'KEY_DIR'}."/".$$info{'CA_NAME'}."/";
    $string_export = "KEY_OU=\"\"; export KEY_OU; KEY_CN=\"\"; export KEY_CN;";
    foreach $k (keys %{$info}) {
	$string_export .= "$k=\"".$$info{$k}."\"; export $k;";
    }
    $string_export .= "KEY_DIR=\"$dir\"; export KEY_DIR;";
    mkdir($dir, 0755) || &error("Failed to create CA directory ".$dir." : $!");
    $wadir = POSIX::getcwd();
    chdir($dir);
    open F,">".$dir."index.txt";
    close F;
    open S,">".$dir."serial";
    print S "01";
    close S;
    unless (&PrintCommandWEB($config{'openssl_path'}." dhparam -out ".$dir."dh".$$info{'KEY_SIZE'}.".pem ".$$info{'KEY_SIZE'},"openssl dhparam -out ".$dir."dh".$$info{'KEY_SIZE'}.".pem ".$$info{'KEY_SIZE'})) {
	rmdir($dir); &error("Failed to create CA ".$$info{'KEY_DIR'}."/".$$info{'CA_NAME'}." : $!");
    } 
    unless (&PrintCommandWEB($string_export." ".$config{'openssl_path'}." req -batch -days ".$$info{'CA_EXPIRE'}." -nodes -new -x509 -keyout \"ca.key\" -out \"ca.crt\" -config ".$$info{'KEY_CONFIG'},$config{'openssl_path'}." req -batch -days ".$$info{'CA_EXPIRE'}." -nodes -new -x509 -keyout \"ca.key\" -out \"ca.crt\" -config ".$$info{'KEY_CONFIG'})) {
	unlink(<$dir*>); rmdir($dir); &error("Failed to create CA ".$$info{'KEY_DIR'}."/".$$info{'CA_NAME'}." : $!");
    }
    unless (&PrintCommandWEB($string_export." ".$config{'openssl_path'}." ca -gencrl -keyfile \"ca.key\" -cert \"ca.crt\" -out \"crl.pem\" -config ".$$info{'KEY_CONFIG'},$config{'openssl_path'}." ca -gencrl -keyfile \"ca.key\" -cert \"ca.crt\" -out \"crl.pem\" -config ".$$info{'KEY_CONFIG'})) {
	unlink(<$dir*>); rmdir($dir); &error("Failed to create CA ".$$info{'KEY_DIR'}."/".$$info{'CA_NAME'}." : $!");
    }
    chmod(0600,$dir."ca.key");
    chmod(0644,$dir."crl.pem");
    if (system("cat ca.crt ca.key > ca.pem")) {
	unlink(<$dir*>); rmdir($dir); &error("Failed to generate ".$dir."ca.pem: $!");
    }
    chmod(0600,$dir."ca.pem");
    chdir($wadir);
}

# Crea la chiave
sub create_key {
    local ($info,$dir,$string_export,$wadir);
    $info = $_[0];
    $dir = $$info{'KEY_DIR'}.'/'.$$info{'KEY_NAME'};
    $string_export = "";
    foreach $k (keys %{$info}) {
	$string_export .= "$k=\"".$$info{$k}."\"; export $k;";
    }
    $wadir = POSIX::getcwd();
    chdir($$info{'KEY_DIR'});
    # server
    if ($$info{'KEY_SERVER'} == 1) {
	unless (&PrintCommandWEB($string_export."openssl req -days ".$$info{'KEY_EXPIRE'}." -batch -new -keyout ".$dir.".key -out ".$dir.".csr -nodes -extensions server -config ".$$info{'KEY_CONFIG'},"openssl req -days ".$$info{'KEY_EXPIRE'}." -batch -new -keyout ".$dir.".key -out ".$dir.".csr -nodes -extensions server -config ".$$info{'KEY_CONFIG'})) {
	    unlink(<$dir.*>); &error("Failed to create key ".$$info{'KEY_NAME'}." : $!");
	}
	unless (&PrintCommandWEB($string_export."openssl ca -days ".$$info{'KEY_EXPIRE'}." -batch -out ".$dir.".crt -in ".$dir.".csr -extensions server -config ".$$info{'KEY_CONFIG'},"openssl ca -days ".$$info{'KEY_EXPIRE'}." -batch -out ".$dir.".crt -in ".$dir.".csr -extensions server -config ".$$info{'KEY_CONFIG'})) {
	    unlink(<$dir.*>); &error("Failed to create key ".$$info{'KEY_NAME'}." : $!");
	}
	if ($$info{'KEY_PKCS12'} eq 2) {
	    unless (&PrintCommandWEB("openssl pkcs12 -export -passout pass:\"".$$info{'KEY_PKCS12_PASSWD'}."\" -inkey ".$$info{'KEY_NAME'}.".key -in ".$$info{'KEY_NAME'}.".crt -certfile ca.crt -out ".$$info{'KEY_NAME'}.".p12","openssl pkcs12 -export -passout pass:\"******\" -inkey ".$$info{'KEY_NAME'}.".key -in ".$$info{'KEY_NAME'}.".crt -certfile ca.crt -out ".$$info{'KEY_NAME'}.".p12")) {
		unlink(<$dir.*>); &error("Failed to create pkcs12 key ".$$info{'KEY_NAME'}." : $!");
	    }
	    chmod(0600,$dir.$$info{'KEY_NAME'}.".p12");
	}
    # client
    } else {
	if ($$info{'KEY_PASSWD'}) {
	    unless (&PrintCommandWEB($string_export."openssl req -days ".$$info{'KEY_EXPIRE'}." -batch -new -keyout ".$dir.".key -out ".$dir.".csr -passout pass:\"".$$info{'KEY_PASSWD'}."\" -config ".$$info{'KEY_CONFIG'},"openssl req -days ".$$info{'KEY_EXPIRE'}." -batch -new -keyout ".$dir.".key -out ".$dir.".csr -passout pass:\"******\" -config ".$$info{'KEY_CONFIG'})) {
		unlink(<$dir.*>); &error("Failed to create key ".$$info{'KEY_NAME'}." : $!");
	    }
	} else {
	    unless (&PrintCommandWEB($string_export."openssl req -days ".$$info{'KEY_EXPIRE'}." -batch -new -keyout ".$dir.".key -out ".$dir.".csr -nodes -config ".$$info{'KEY_CONFIG'},"openssl req -days ".$$info{'KEY_EXPIRE'}." -batch -new -keyout ".$dir.".key -out ".$dir.".csr -nodes -config ".$$info{'KEY_CONFIG'})) {
		unlink(<$dir.*>); &error("Failed to create key ".$$info{'KEY_NAME'}." : $!");
	    }
	}
	unless (&PrintCommandWEB($string_export."openssl ca -days ".$$info{'KEY_EXPIRE'}." -batch -out ".$dir.".crt -in ".$dir.".csr -config ".$$info{'KEY_CONFIG'},"openssl ca -days ".$$info{'KEY_EXPIRE'}." -batch -out ".$dir.".crt -in ".$dir.".csr -config ".$$info{'KEY_CONFIG'})) {
	    unlink(<$dir.*>); &error("Failed to create key ".$$info{'KEY_NAME'}." : $!");
	}
	if ($$info{'KEY_PKCS12'} eq 2) {
	    if ($$info{'KEY_PKCS12_PASSWD'} and $$info{'KEY_PASSWD'}) {
		unless (&PrintCommandWEB("openssl pkcs12 -export -passout pass:\"".$$info{'KEY_PKCS12_PASSWD'}."\" -inkey ".$$info{'KEY_NAME'}.".key -passin pass:\"".$$info{'KEY_PASSWD'}."\" -in ".$$info{'KEY_NAME'}.".crt -certfile ca.crt -out ".$$info{'KEY_NAME'}.".p12","openssl pkcs12 -export -passout pass:\"******\" -inkey ".$$info{'KEY_NAME'}.".key -passin pass:\"******\" -in ".$$info{'KEY_NAME'}.".crt -certfile ca.crt -out ".$$info{'KEY_NAME'}.".p12")) {
		    unlink(<$dir.*>); &error("Failed to create pkcs12 key ".$$info{'KEY_NAME'}." : $!");
		}
	    }
	    chmod(0600,$dir.$$info{'KEY_NAME'}.".p12");
	}
    }
    chmod(0600,$dir.$$info{'KEY_NAME'}.".key");
    chmod(0600,$dir.$$info{'KEY_NAME'}.".crt");
    chmod(0600,$dir.$$info{'KEY_NAME'}.".csr");
    chdir($wadir);
}

# Verifica la CA
sub verify_CA {
    local ($file_name,$dir,$wadir);
    $file_name = $_[0];
    $dir = $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'}.'/'.$file_name.'/';
    $wadir = POSIX::getcwd();
    chdir($dir);
    if (-s $dir."ca.pem") {
	unless (&PrintCommandWEB("openssl x509 -noout -fingerprint -text < ca.pem","openssl x509 -noout -fingerprint -text < ca.pem")) {
	    &error("Failed to verify CA ".$file_name." : $!");
	} 
    } else {
	&error("Failed to verify CA ".$file_name." : file ca.pem not found");
    }
    chdir($wadir);
}

# Verifica la key
sub verify_key {
    local ($info,$dir,$wadir);
    $info = $_[0];
    $dir = $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'}.'/'.$$info{'ca_name'}.'/';
    $wadir = POSIX::getcwd();
    chdir($dir);
    if (-s $dir."ca.pem" and $dir.$$info{'key_id'}.".pem") {
	unless (&PrintCommandWEB("openssl verify -CAfile ca.pem ".$$info{'key_id'}.".pem",$$info{key_name}.": openssl verify -CAfile ca.pem ".$$info{'key_id'}.".pem")) {
	    &error("Failed to verify key ".$$info{key_name}." : $!");
	} 
    } else {
	&error("Failed to verify key ".$$info{key_name}." : file ca.pem not found");
    }
    chdir($wadir);
}

# Vista di key
sub view_key {
    local ($file_name,$dir,$wadir);
    $info = $_[0];
    $dir = $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'}.'/'.$$info{'ca_name'}.'/';
    $wadir = POSIX::getcwd();
    chdir($dir);
    if (-s $dir.$$info{'key_id'}.".pem") {
	unless (&PrintCommandWEB("openssl x509 -noout -fingerprint -text < ".$$info{'key_id'}.".pem",$$info{key_name}.": openssl x509 -noout -fingerprint -text < ".$$info{'key_id'}.".pem")) {
	    &error("Failed to view key ".$$info{'key_name'}." : $!");
	} 
    } else {
	&error("Failed to view key ".$$info{'key_name'}." : file ".$$info{'key_id'}.".pem not found");
    }
    chdir($wadir);
}

# Revoca la key
sub revoke_key {
    local ($info,$dir,$wadir,$string_export,$k);
    $info = $_[0];
    $dir = $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'}.'/'.$$info{'ca_name'}.'/';
    $string_export = "KEY_OU=\"\"; export KEY_OU; KEY_CN=\"\"; export KEY_CN;";
    $$info_ca{'KEY_DIR'} = $$info_ca{'KEY_DIR'}.'/'.$$info{'ca_name'};
    foreach $k (keys %{$info_ca}) {
	$string_export .= "$k=\"".$$info_ca{$k}."\"; export $k;";
    }
    $wadir = POSIX::getcwd();
    chdir($dir);
    if (-s $dir.$$info{'key_name'}.".crt") {
	if (-f $dir."revoke-test.pem") { unlink($dir."revoke-test.pem"); }
	unless (&PrintCommandWEB($string_export."openssl ca -revoke \"".$$info{'key_name'}.".crt\" -config \"".$$info_ca{'KEY_CONFIG'}."\"","openssl ca -revoke \"".$$info{'key_name'}.".crt\" -config \"".$$info_ca{'KEY_CONFIG'}."\"")) {
	    &error("Failed to revoke key ".$$info{'key_name'}." : $!");
	} 
	unless (&PrintCommandWEB($string_export."openssl ca -gencrl -out \"crl.pem\" -config \"".$$info_ca{'KEY_CONFIG'}."\"","openssl ca -gencrl -out \"crl.pem\" -config \"".$$info_ca{'KEY_CONFIG'}."\"")) {
	    &error("Failed to revoke key ".$$info{'key_name'}." : $!");
	}
	unless (&PrintCommandWEB("cat ca.crt \"crl.pem\" >\"revoke-test.pem\"","cat ca.crt \"crl.pem\" >\"revoke-test.pem\"")) {
	    &error("Failed to revoke key ".$$info{'key_name'}." : $!");
	}
	unless (&PrintCommandWEB("openssl verify -CAfile \"revoke-test.pem\" -crl_check \"".$$info{'key_name'}.".crt\"","openssl verify -CAfile \"revoke-test.pem\" -crl_check \"".$$info{'key_name'}.crt."\"")) {
	    &error("Failed to revoke key ".$$info{'key_name'}." : $!");
	}
	print "<strong>".$text{'error23'}."</strong><BR><BR>";
    } else {
	&remove_key($info,1);
	&error("Absent crt: forced key ".$$info{'key_name'}." removal!");
    }
    chdir($wadir);
}

# Rimouove la key se revocata, altrimenti la revoca e poi la rimuove
sub remove_key {
    local ($info,$dir,$wadir,$string,$ok);
    $info = $_[0];
    $force = $_[1];
    $dir = $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'}.'/'.$$info{'ca_name'}.'/';
    if (-s $dir."index.txt") {
	open IN,$dir."index.txt";
	$ok = 0;
	while ($row=<IN>) {
	    $cakeys = {};
	    $row =~ s/\r*\n//g;
	    ($$cakeys{key_status},$$cakeys{key_expired},$$cakeys{key_revoked},$$cakeys{key_id},$$cakeys{key_unknow},$$cakeys{key_string}) = split(/\t/,$row);
	    if ($$cakeys{key_id} eq $$info{'key_id'} and ($$cakeys{key_status} eq "R" or $force == 1)) { $ok = 1; } 
	    else { $string .= $row."\n"; }
	}
	close IN;
	if ($ok == 0) { 
	    &revoke_key($info);
	    $string = "";
	    $ok = 0;
	    open IN,$dir."index.txt";
	    while ($row=<IN>) {
		$cakeys = {};
		$row =~ s/\r*\n//g;
		($$cakeys{key_status},$$cakeys{key_expired},$$cakeys{key_revoked},$$cakeys{key_id},$$cakeys{key_unknow},$$cakeys{key_string}) = split(/\t/,$row);
		if ($$cakeys{key_id} eq $$info{'key_id'} and ($$cakeys{key_status} eq "R" or $force == 1)) { $ok = 1; } 
		else { $string .= $row."\n"; }
	    }
	    close IN;
	}    
	if ($ok == 1) {
	    open OUT,">".$dir."index.txt";
	    print OUT $string; 	
	    close OUT;
	    $dir .= $$info{'key_name'};
	    unlink(<$dir.*>);
	    return(1);
	} else {
	    return(0);
	}
    }
}

sub disconnect_client {
    local ($info,$error);
    $info=$_[0];
    &open_socket($$info{'management_url'}, $$info{'management_port'}, MAIL, \$error);
    if ($error) { return($error); }
    print MAIL "kill ".$$info{'CLIENT_NAME'}."\r\n";
    print MAIL "quit\r\n";
    return(0);
}

sub ReadCA {
    local ($dir,$d,@dirs,%outca);
    $dir = $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'};
    opendir(D,$dir);
    @dirs = readdir D;
    foreach $d (sort @dirs) {
        if (-d $dir."/".$d and $d =~ /\w/) {
	    $outca{$d} = { ca_path => $dir."/".$d, ca_name => $d , ca_error => "" };
	    if (!-s $dir."/".$d."/ca.crt" or !-s $dir."/".$d."/ca.key" or !-s $dir."/".$d."/ca.pem") { $outca{$d}{ca_error} = $text{'error_correctly_ca'}; next; }
	    if (!-s $dir."/".$d."/dh2048.pem" and !-s $dir."/".$d."/dh4096.pem") { $outca{$d}{ca_error} = $text{'error_correctly_ca'}; next; }
	    if (!$outca{$d}{ca_error}) { $outca{$d}{ca_error} = "&nbsp;"; }
        }
    }
    closedir D;
    return(\%outca);
}

sub ReadCAtoList {
    local ($dir,$d,@dirs,@outca);
    $dir = $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'};
    opendir(D,$dir);
    @dirs = readdir D;
    foreach $d (sort @dirs) {
        if (-d $dir."/".$d and $d =~ /\w/) {
	    if (!-s $dir."/".$d."/ca.crt" or !-s $dir."/".$d."/ca.key" or !-s $dir."/".$d."/ca.pem") { next; }
	    if (!-s $dir."/".$d."/dh2048.pem" and !-s $dir."/".$d."/dh4096.pem") {  next; }
	    push (@outca,[$d,$d]);
        }
    }
    closedir D;
    return(\@outca);
}

# legge file ca.config con informazioni circa la ca per la fiunestra di view della stessa
sub ReadFieldsCA {
    local ($file_name,$dir,$row);
    $file_name =$_[0];
    $info_ca = {};
    $dir = $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'}.'/'.$file_name.'/';
    if (-s $dir."ca.config") { do $dir."ca.config"; }
}

# legge elenco chiavi per la CA passata (legge file index.txt)
sub ReadCAKeys {
    local ($active,$type,$file_name,$dir,$row,$cakeys,$time,$mytime,$keys_news,
	$ok_active,$mystring,$data,$name,$value,$vpn_name,%cakeysout,@outca,@data_string);
    $file_name =$_[0];
    # $type = 
    # - 0 (lista tutte le chiavi come hash [con chiave primaria key_id]), 
    # - 1 (lista chiavi come array per liste),
    # - 2 (lista chiavi server come array per liste),
    # - 3 (lista chiavi client come array per liste),
    $type = $_[1];
    # se 1 solo le attive, se 0 tutte
    $active = $_[2];
    # se 1 solo quelle ancora non utilizzate, se 0 tutte
    $keys_news = $_[3];
    # se presente, solo quelle non utilizzate dalla vpn (con $keys_news=1 e $type=3)
    if ($_[4]) { $vpn_name = $_[4]; } else { $vpn_name = ""; }
    %cakeysout = ();
    @outca=();
    $dir = $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'}.'/'.$file_name.'/index.txt';
    if (-s $dir) {
	open IN,$dir;
	while ($row=<IN>) {
	    $ok_active = 0;
	    $cakeys = {};
	    $row =~ s/\r*\n//g;
	    ($$cakeys{key_status},$$cakeys{key_expired},$$cakeys{key_revoked},$$cakeys{key_id},$$cakeys{key_unknow},$$cakeys{key_string}) = split(/\t/,$row);
	    $mystring = $$cakeys{key_string};
	    $mystring =~ s/^\///;	    
	    $mystring =~ s/\/$//;	    
	    @data_string = split(/\//,$mystring);
	    foreach $data (@data_string) {
		($name,$value) = split("=",$data);
		if ($name =~ /^c$/i) { $$cakeys{key_c} = $value; }
		elsif ($name =~ /^st$/i) { $$cakeys{key_st} = $value; } 
		elsif ($name =~ /^l$/i) { $$cakeys{key_st} = $value; } 
		elsif ($name =~ /^o$/i) { $$cakeys{key_o} = $value; } 
		elsif ($name =~ /^ou$/i) { $$cakeys{key_ou} = $value; } 
		elsif ($name =~ /^cn$/i) { $$cakeys{key_name} = $value; } 
		elsif ($name =~ /^emailaddress$/i) { $$cakeys{key_email} = $value; } 
	    }	
	    if ($type == 0 or !$type) {
		$cakeysout{$$cakeys{key_id}} = $cakeys;
	    } elsif ($type == 1 
		or ($type == 2 and -s $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'}.'/'.$file_name.'/'.$$cakeys{key_name}.'.server')
		or ($type == 3 and !-s $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'}.'/'.$file_name.'/'.$$cakeys{key_name}.'.server')) {
		if ($active == 1) {
    		    if ($$cakeys{key_expired} =~ /^\d{12}Z$/) {
        		$$cakeys{key_expired} =~ /^(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)Z$/;
        		$time = Time::Local::timegm($6,$5,$4,$3,($2-1),"20".$1);
    		    } elsif ($$cakeys{key_expired} =~ /^\d{14}Z$/) {
        		$$cakeys{key_expired} =~ /^(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)Z$/;
        		$time = Time::Local::timegm($7,$5,$4,$3,($2-1),$1);
    		    }
    		    $mytime = time();
		    if ($$cakeys{key_status} ne 'R' and $time > $mytime) {
			$ok_active = 1;
		    }
		} else {
		    $ok_active = 1;
		}
		if ($ok_active == 1) {
		    if ($keys_news == 1 and $type == 3) {
			$not_ok = 0;
			opendir D,$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'};
			@dirs = readdir D;
			closedir D;
			foreach $dir (@dirs) {
			    if (-d $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$dir and $dir =~ /\w/) {
				if (-d $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$dir.'/'.$$cakeys{key_name}) {
				    if (($vpn_name and $vpn_name eq $dir) or !$vpn_name) { $not_ok = 1; last; }
				} 
			    }
			}
			if ($not_ok == 0) { push(@outca,[$$cakeys{key_name},$$cakeys{key_name}]); }
		    } else {
			push(@outca,[$$cakeys{key_name},$$cakeys{key_name}]);
		    }
		}
	    }
	}
	close IN;
    }
    if ($type == 0) {
	return(\%cakeysout);
    } elsif ($type == 1 or $type == 2 or $type == 3) {
	return(\@outca);
    }
}

# array derivante da comando 'openvpn --show-ciphers': il valore e' il primo campo ed etichetta tutto
sub ReadCiphers {
   local ($row,$key,$a_cypher);
    $a_cypher = [];
    &open_execute_command(CMD, $config{'openvpn_path'} . ' --show-ciphers', 2);
    while ($row=<CMD>) {
        $row =~ s/\r*\n//g;
        if (($row =~ /bit default key/i) or ($row =~ /bit key/i) or ($row =~ /bit key by default/i)) {
            ($key) = split(' ',$row);
            push(@$a_cypher,[$key,$row]);
        }
    }
    close(CMD);
    return($a_cypher);
}

# array of aviable ethernet devices
sub ReadEths {
    local ($row,$a_eth,$dev);
    $dev = $_[0];
    $a_eth = [];
    &open_execute_command(CMD, 'ip -o link | grep -i link/ether |awk \'{print substr($2, 1, length($2)-1)}\'', 2);
#    &open_execute_command(CMD, 'ifconfig|grep -i "[:(]ethernet" |awk \'{print $1}\'', 2);
    while ($row=<CMD>) {
	$row =~ s/\r*\n//g;
	if (($row ne $dev) && ($row !~ /^tap\d+/)) {
    	    push(@$a_eth,[$row,$row]);
	}
    }
    close(CMD);
    return($a_eth);
}

# rimuove files e directory della CA
sub remove_CA {
    local ($file_name,$dir,$row);
    $file_name =$_[0];
    $dir = $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'}.'/'.$file_name.'/';
    unlink(<$dir*>); 
    unless(rmdir($dir)) { &error("Failed to remove CA $file_name: $!"); };
}

# rimuove files e directory del client
sub remove_client {
    local ($client,$dir,$vpn);
    $client =$_[0];
    $vpn=$_[1];
    $dir = $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$vpn.'/'.$client.'/';
    unlink(<$dir*>); 
    unlink($config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$vpn.'/ccd/'.$client);
    unless(rmdir($dir)) { &error("Failed to remove client $client: $!"); };
}

# rimuove files e directory della vpn
sub remove_vpn {
    local ($vpn);
    $vpn=$_[0];
    &system_logged("rm -rf ".$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$vpn." >/dev/null 2>&1 </dev/null");
    if (-f $config{'openvpn_home'}.'/'.$vpn.'.conf') { unlink($config{'openvpn_home'}.'/'.$vpn.'.conf'); }
    if (-f $config{'openvpn_home'}.'/'.$vpn.'.disabled') { unlink($config{'openvpn_home'}.'/'.$vpn.'.disabled'); }
    rmdir($config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$vpn);
}

# rimuove files e directory della vpn
sub remove_static_vpn {
    local ($vpn);
    $vpn=$_[0];
    &system_logged("rm -rf ".$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$vpn." >/dev/null 2>&1 </dev/null");
    &system_logged("rm -rf ".$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$vpn." >/dev/null 2>&1 </dev/null");
    if (-f $config{'openvpn_home'}.'/'.$vpn.'.conf') { unlink($config{'openvpn_home'}.'/'.$vpn.'.conf'); }
    if (-f $config{'openvpn_home'}.'/'.$vpn.'.disabled') { unlink($config{'openvpn_home'}.'/'.$vpn.'.disabled'); }
    if (-f $config{'openvpn_home'}.'/'.$vpn.'.key') { unlink($config{'openvpn_home'}.'/'.$vpn.'.key'); }
}

sub ReadVPN {
    local ($file,$row,$datas,@files,%vpns,%vpns_static);
    $only_managed = $_[0];
    opendir D,$config{'openvpn_home'};
    @files = readdir D;
    closedir D;
    %vpns=();
    %vpns_static=();	
    foreach $file (@files) {
	if ($file =~ /\.conf$/ or $file =~ /\.disabled$/) {
	    if ($file =~ /\.conf$/) { $file =~ /^(.+)\.conf/; $namefile = $1; }
	    elsif ($file =~ /\.disabled$/) { $file =~ /^(.+)\.disabled/; $namefile = $1; }
	    $datas = {};
	    $$datas{'VPN_NAME'} = $namefile;
	    open F,$config{'openvpn_home'}.'/'.$file;
	    while ($row=<F>) {
		$row =~ s/\r*\n//g;
		$row =~ s/;.+$//;
		$row =~ s/#.+$//; #commento
		if ($row) {
		    $row =~ /^(\S+)\s+(.+)$/;
		    $$datas{$1} = $2;
		}
	    }
	    close F;

	    if ($file =~ /\.conf$/) { $$datas{'VPN_STATUS'} = 1; } else { $$datas{'VPN_STATUS'} = 0; }
            # Versione originale
            # if (-s $config{'openvpn_pid_path'}.'/openvpn.'.$namefile.'.pid') { $$datas{'VPN_ACTION'} = 1; } else { $$datas{'VPN_ACTION'} = 0; }
            # Versione configurabile
            #if (-s $config{'openvpn_pid_path'}.'/'.$config{'openvpn_pid_prefix'}.$namefile.'.pid') { $$datas{'VPN_ACTION'} = 1; } else { $$datas{'VPN_ACTION'} = 0; }
	    if (&system_logged(sprintf($config{'status_cmd'},$$datas{'VPN_NAME'}))) { $$datas{'VPN_ACTION'} = 0; } else { $$datas{'VPN_ACTION'} = 1; }

	    if ($only_managed == 1 and !exists($$datas{'management'})) { next; }
	    if (exists($$datas{'secret'})) { $vpns_static{$$datas{'VPN_NAME'}} = $datas; } 
	    else { 
		$$datas{'ca'} =~ /$config{'openvpn_keys_subdir'}\/(.+)\/ca\.crt$/;
		$$datas{'CA_NAME'} = $1;
		$vpns{$$datas{'VPN_NAME'}} = $datas; 
	    }
	}
    }
    return(\%vpns,\%vpns_static);
}

sub ReadConnections {
    local($vpn,$management_url,$management_port,$error,$got,$rows,$list_conn,@fields);
    $vpn = $_[0];
    $management_url = $_[1];
    $management_port = $_[2];
    $list_conn = {};
    $error = "";
    &open_socket($management_url, $management_port, MAIL, \$error);
    if ($error) { return({},$error); }
    print MAIL "status\r\n";
    $prime_righe = 0;
    $seconde_righe = 0;
    while ($row = <MAIL>) {
	$row =~ s/\r*\n//g;
	if ($row eq "Common Name,Real Address,Bytes Received,Bytes Sent,Connected Since") {
	    $prime_righe = 1; $seconde_righe = 0;
	} elsif ($row eq "ROUTING TABLE") {
	    $prime_righe = 0; $seconde_righe = 0;
	} elsif ($row eq "Virtual Address,Common Name,Real Address,Last Ref") {
	    $prime_righe = 0; $seconde_righe = 1;
	} elsif ($row eq "GLOBAL STATS") {
	    $prime_righe = 0; $seconde_righe = 0; last;
	} elsif ($prime_righe == 1) {
	    @fields = split(',',$row);
     	    $$list_conn{$fields[0]}{real_address} = $fields[1];
	    $$list_conn{$fields[0]}{bytes_received} = $fields[2];
	    $$list_conn{$fields[0]}{bytes_sent} = $fields[3]; 
	    $$list_conn{$fields[0]}{connected_since} = $fields[4];
	} elsif ($seconde_righe == 1) {
	    @fields = split(',',$row);
     	    $$list_conn{$fields[1]}{virtual_address} = $fields[0];
	    if (!$list_conn{$fields[0]}{real_address}) { $list_conn{$fields[0]}{real_address} = $fields[2]; }
	    $$list_conn{$fields[1]}{last_ref} = $fields[3];
	}
    }
    print MAIL "quit\r\n";
    return($list_conn,'');
}

sub ReadStaticConnections {
    local($vpn,$management_url,$management_port,$error,$got,$rows,$list_conn,@fields);
    $vpn = $_[0];
    $management_url = $_[1];
    $management_port = $_[2];
    $list_conn = {};
    $error = "";
    &open_socket($management_url, $management_port, MAIL, \$error);
    if ($error) { return({},$error); }
    print MAIL "status\r\n";
    $prime_righe = 0;
    $seconde_righe = 0;
    while ($row = <MAIL>) {
	$row =~ s/\r*\n//g;
	if ($row eq "Common Name,Real Address,Bytes Received,Bytes Sent,Connected Since") {
	    $prime_righe = 1; $seconde_righe = 0;
	} elsif ($row eq "ROUTING TABLE") {
	    $prime_righe = 0; $seconde_righe = 0;
	} elsif ($row eq "Virtual Address,Common Name,Real Address,Last Ref") {
	    $prime_righe = 0; $seconde_righe = 1;
	} elsif ($row eq "GLOBAL STATS" or $row eq "END") {
	    $prime_righe = 0; $seconde_righe = 0; last;
	} elsif ($prime_righe == 1) {
	    @fields = split(',',$row);
     	    $$list_conn{$fields[0]}{real_address} = $fields[1];
	    $$list_conn{$fields[0]}{bytes_received} = $fields[2];
	    $$list_conn{$fields[0]}{bytes_sent} = $fields[3]; 
	    $$list_conn{$fields[0]}{connected_since} = $fields[4];
	} elsif ($seconde_righe == 1) {
	    @fields = split(',',$row);
     	    $$list_conn{$fields[1]}{virtual_address} = $fields[0];
	    if (!$list_conn{$fields[0]}{real_address}) { $list_conn{$fields[0]}{real_address} = $fields[2]; }
	    $$list_conn{$fields[1]}{last_ref} = $fields[3];
	}
    }
    print MAIL "quit\r\n";
    return($list_conn,'');
}

sub ReadClient {
    local ($file,$row,$datas,@files,%vpns);
    opendir D,$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'};
    @files = readdir D;
    closedir D;
    %vpns=();
    foreach $file (@files) {
	if (-d $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$file and $file =~ /\w/ and -f $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$file.'/'.$file.'.conf') {
	    $datas = {};
	    $$datas{'VPN_NAME'} = $in{'vpn'};
	    $$datas{'CLIENT_NAME'} = $file;
	    open F,$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$file.'/'.$file.'.conf';
	    while ($row=<F>) {
		$row =~ s/\r*\n//g;
		$row =~ s/;.+$//;
		$row =~ s/#.+$//; #commento
		if ($row) {
		    $row =~ /^(\S+)\s+(.+)$/;
		    $$datas{$1} = $2;
		}
	    }
	    close F;
	    if (-s $config{'openvpn_home'}.'/'.$in{'vpn'}.'.conf') {
		open S,$config{'openvpn_home'}.'/'.$in{'vpn'}.'.conf';
	    } elsif (-s $config{'openvpn_home'}.'/'.$in{'vpn'}.'.disabled') {
		open S,$config{'openvpn_home'}.'/'.$in{'vpn'}.'.disabled';
	    }
	    while ($row=<S>) {
		$row =~ s/\r*\n//g;
		$row =~ s/;.+$//;
		$row =~ s/#.+$//; #commento
		if ($row and $row =~ /^ca\s+/) {
		    $row =~ /^(\S+)\s+(.+)$/;
		    $$datas{$1} = $2;
		    last;
		}
	    }
	    close S;
	    $$datas{'ca'} =~ /$config{'openvpn_keys_subdir'}\/(.+)\/ca\.crt$/;
	    $$datas{'CA_NAME'} = $1;
	    $vpns{$$datas{'CLIENT_NAME'}} = $datas; 
	}
    }
    return(\%vpns);
}

# lettura file config di vpn
sub ReadVPNConf {
    local ($namefile,$row,$key,$value,$text,$key_commands,$key_normal,$key_skip,$key_key);
    if (-s $config{'openvpn_home'}.'/'.$in{'vpn'}.'.conf') {
	$namefile = $config{'openvpn_home'}.'/'.$in{'vpn'}.'.conf';
    } elsif (-s $config{'openvpn_home'}.'/'.$in{'vpn'}.'.disabled') {
	$namefile = $config{'openvpn_home'}.'/'.$in{'vpn'}.'.disabled';
    }
    open F, $namefile;
    $key_normal = ",port,proto,dev,cipher,max-clients,user,group,verb,mute,fragment,tun-mtu,mssfix,chroot,local,topology,log-append,status,";
    $key_skip= ",ca,cert,dh,status,log-append,crl-verify,client-config-dir,";
    $key_commands= ",up,down,up-pre,down-pre,";
    $down_root_plugin= $config{'down_root_plugin'}.' ';
    $key_key= ",tls-server,ifconfig-pool-persist,client-to-client,duplicate-cn,tls-auth,comp-lzo,persist-key,persist-tun,float,ccd-exclusive,";
    while ($row=<F>) {
	$row =~ s/\r*\n//g;
	$row =~ s/^;.+$//;
	$row =~ s/^#.+$//; #commento
	# le opzioni 'plugin' non verranno trascurate
	#$row =~ s/^plugin.*$//; #plugins only used by me for down-root-script-solution
	$row =~ s/\s+$//;
	if ($row) {
	    if ($row =~ /\s/) {
		$row =~ /^(\S+)\s+(.+)$/;
		$key = $1;
		$value = $2; 
	    } else {
		$key = $row;
		$value = "";
	    }
	    if ($key_normal =~ /,$key,/) {
		$in{$key} = $value;
	    } elsif ($key eq "key") {
		$value =~ /^$config{'openvpn_keys_subdir'}\/([^\/]+)\/([^\/]+)\.key$/;
		$in{'ca'} = $1;
		$in{'choose_server'} = $2;
	    } elsif (($key eq "server-bridge")) {
		$value =~ /^(.+)\s+(.+)\s+(.+)\s+(.+)\s+#@@\s+(.+)\s+(.+)$/;
		$in{'ipbr'} = $1;
		$in{'netmaskbr'} = $2;
		$in{'iprangestart'} = $3;
		$in{'iprangeend'} = $4;
		$in{'devbr'} = $5;
		$in{'netdevbr'} = $6;
	    } elsif (($key eq "server")) {
		$value =~ /^(.+)\s+(.+)$/;
		$in{'network'} = $1;
		$in{'netmask'} = $2;
	    } elsif ($key eq "management") {
		$value =~ /^(.+)\s+(.+)$/;
		$in{'management'} = 1;
		$in{'management_url'} = $1;
		$in{'management_port'} = $2;
	    } elsif ($key eq "keepalive") {
		$value =~ /^(.+)\s+(.+)$/;
		$in{'keepalive_ping'} = $1;
		$in{'keepalive_ping-restart'} = $2;
            } elsif (($key eq "plugin") && $value =~ /^$config{'down_root_plugin'}/ && $config{'down_root_plugin'}) {
                $key = 'down-root';
                $value =~ s/^$config{'down_root_plugin'}\s+//;  # estrae il nome dello script
                $value =~ s/"//g; #" 				# elimina le virgolette!!!
        	$text="";
                if ($value) {
                    if (-s $value) {
                        open U,$value;
                        while ($row=<U>) { $text .= $row; }
                        close U;
                        $text =~ s/\r+//g;
			#
			# cut off our commands
                        $text =~ s/.*##### add your commands below #####$//smg;
            		$in{$key} = $text;
                    } else {
                        delete($in{$key});
                    }
                }
	    } elsif ($key_commands =~ /,$key,/) {
		$text="";
		if ($value) {
		    if (-s $config{'openvpn_home'}.'/'.$value) {
			open U,$config{'openvpn_home'}.'/'.$value;
			while ($row=<U>) { $text .= $row; }
			close U;	
			$in{$key} = $text;
			$in{$key} =~ s/\r+//g;
			#
			# cut of our commands
			$in{$key} =~ s/.*##### add your commands below #####$//smg;
		    } else {
			delete($in{$key});
		    }
		}
	    } elsif ($key_key =~ /,$key,/) {
		$in{$key} = 1;
		$in{$key."-old"} = $value;
	    } elsif ($key_skip =~ /,$key,/) {
		next;
	    } else {
		# ora tra le configurazioni addizionali può essere specificato 
		# anche un plugin purché diverso da quello di down-root
		$in{'adds_conf'} .= $row."\n";
	    }
	}
    }
    close F;
}

# lettura file config di vpn
sub ReadStaticVPNConf {
    local ($namefile,$row,$key,$value,$text,$key_commands,$key_normal,$key_skip,$key_key);
    if (-s $config{'openvpn_home'}.'/'.$in{'vpn'}.'.conf') {
	$namefile = $config{'openvpn_home'}.'/'.$in{'vpn'}.'.conf';
    } elsif (-s $config{'openvpn_home'}.'/'.$in{'vpn'}.'.disabled') {
	$namefile = $config{'openvpn_home'}.'/'.$in{'vpn'}.'.disabled';
    }
    open F, $namefile;
    $key_normal = ",port,proto,dev,user,group,verb,mute,topology,log-append,status,";
    #$key_skip= ",status,log-append,secret,";
    $key_commands= ",up,down,";
    $key_key= ",comp-lzo,persist-key,persist-tun,";
    $in{'client-nat'} = 1;
    while ($row=<F>) {
	$row =~ s/\r*\n//g;
	$row =~ s/;.+$//;
	$row =~ s/#.+$//; #commento
	$row =~ s/\s+$//;
	if ($row) {
	    if ($row =~ /\s/) {
		$row =~ /^(\S+)\s+(.+)$/;
		$key = $1;
		$value = $2; 
	    } else {
		$key = $row;
		$value = "";
	    }
	    if ($key_normal =~ /,$key,/) {
		$in{"vpn_".$key} = $value;
	    } elsif ($key eq "remote") {
		$value =~ /^(.+)\s+(.+)$/;
		$in{'vpn_remote_url'} = $1;
		$in{'vpn_remote_port'} = $2;
		$in{'client-nat'} = 0;
	    } elsif ($key eq "ifconfig") {
		$value =~ /^(.+)\s+(.+)$/;
		$in{'vpn_ifconfig_from'} = $1;
		$in{'vpn_ifconfig_to'} = $2;
	    } elsif ($key eq "management") {
		$value =~ /^(.+)\s+(.+)$/;
		$in{'management'} = 1;
		$in{'management_url'} = $1;
		$in{'management_port'} = $2;
	    } elsif ($key eq "keepalive") {
		$value =~ /^(.+)\s+(.+)$/;
		$in{'vpn_keepalive_ping'} = $1;
		$in{'vpn_keepalive_ping-restart'} = $2;
	    } elsif ($key eq "secret") {
		$secretfile = $config{'openvpn_home'}.'/'. $value;
		open FILE, $secretfile;
                while ($line=<FILE>) {
                    $static_key = $static_key . $line;
                }
		$in{"static_key"} = $static_key;
		close FILE;
	    } elsif ($key_commands =~ /,$key,/) {
		$text="";
		if ($value) {
		    if (-s $config{'openvpn_home'}.'/'.$value) {
			open U,$config{'openvpn_home'}.'/'.$value;
			while ($row=<U>) { $text .= $row; }
			close U;
			$in{"vpn_".$key} = $text;
			$in{"vpn_".$key} =~ s/\r+//g;
		    } else {
			delete($in{"vpn_".$key});
		    }
		}
	    } elsif ($key_key =~ /,$key,/) {
		$in{"vpn_".$key} = 1;
	    } elsif ($key_skip =~ /,$key,/) {
		next;
	    } else {
		$in{'vpn_adds_conf'} .= $row."\n";
	    }
	}
    }
    close F;
    open F, $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'vpn'}.'.conf';
    $key_normal = ",port,verb,mute,";
    $key_skip= ",status,log-append,proto,dev,ifconfig,comp-lzo,user,group,persist-key,persist-tun,keepalive,secret,topology,";
    $key_commands= ",up,down,";
    $key_key= ",";
    while ($row=<F>) {
	$row =~ s/\r*\n//g;
	$row =~ s/;.+$//;
	$row =~ s/#.+$//; #commento
	$row =~ s/\s+$//;
	if ($row) {
	    if ($row =~ /\s/) {
		$row =~ /^(\S+)\s+(.+)$/;
		$key = $1;
		$value = $2; 
	    } else {
		$key = $row;
		$value = "";
	    }
	    if ($key_normal =~ /,$key,/) {
		$in{"client_".$key} = $value;
	    } elsif ($key eq "remote") {
		$value =~ /^(.+)\s+(.+)$/;
		$in{'client_remote_url'} = $1;
		$in{'client_remote_port'} = $2;
	    } elsif ($key_commands =~ /,$key,/) {
		$text="";
		if ($value) {
		    if (-s $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$value) {
			open U,$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$value;
			while ($row=<U>) { $text .= $row; }
			close U;
			$in{"client_".$key} = $text;
			$in{"client_".$key} =~ s/\r+//g;
		    } else {
			delete($in{"client_".$key});
		    }
		}
	    } elsif ($key_key =~ /,$key,/) {
		$in{"client_".$key} = 1;
	    } elsif ($key_skip =~ /,$key,/) {
		next;
	    } else {
		$in{'client_adds_conf'} .= $row."\n";
	    }
	}
    }
    close F;
}

# lettura file config di client
sub ReadClientConf {
    local ($namefile,$row,$key,$value,$text,$key_commands,$key_normal,$key_skip,$key_key);
    $namefile = $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'client'}.'/'.$in{'client'}.'.conf';
    open F, $namefile;
    $key_normal = ",proto,dev,cipher,user,group,verb,mute,fragment,tun-mtu,mssfix,";
    $key_skip= ",cert,key,dh,client,resolv-retry,nobind,";
    $key_commands= ",up,down,up-pre,down-pre,down-root,";
    $key_key= ",tls-auth,comp-lzo,persist-key,persist-tun,float,nobind,resolv-retry,auth-nocache,";
    while ($row=<F>) {
	$row =~ s/\r*\n//g;
	$row =~ s/;.+$//;
	$row =~ s/#.+$//; #commento
	$row =~ s/\s+$//;
	if ($row) {
	    if ($row =~ /\s/) {
		$row =~ /^(\S+)\s+(.+)$/;
		$key = $1;
		$value = $2; 
	    } else {
		$key = $row;
		$value = "";
	    }
	    if ($key_normal =~ /,$key,/) {
		$in{$key} = $value;
	    } elsif ($key eq "ca") {
		if (-s $config{'openvpn_home'}.'/'.$in{'vpn'}.'.conf') {
		    open S,$config{'openvpn_home'}.'/'.$in{'vpn'}.'.conf';
		} elsif (-s $config{'openvpn_home'}.'/'.$in{'vpn'}.'.disabled') {
		    open S,$config{'openvpn_home'}.'/'.$in{'vpn'}.'.disabled';
		}
		while ($myrow=<S>) {
		    $myrow =~ s/\r*\n//g;
		    $myrow =~ s/;.+$//;
		    $myrow =~ s/#.+$//; #commento
		    if ($myrow and $myrow =~ /^ca\s+/) {
			$myrow =~ /ca\s+(.+)$/;
			$value = $1;
			last;
		    }
		}
		close S;
		$value =~ /$config{'openvpn_keys_subdir'}\/(.+)\/ca\.crt$/;
		$in{'CA_NAME'} = $1;
		$in{'ca'} = $in{'CA_NAME'};
	    } elsif ($key eq "remote") {
		$value =~ /^(.+)\s+(.+)$/;
		$in{'remote_url'} = $1;
		$in{'remote_port'} = $2;
	    } elsif ($key eq "keepalive") {
		$value =~ /^(.+)\s+(.+)$/;
		$in{'keepalive_ping'} = $1;
		$in{'keepalive_ping-restart'} = $2;
	    } elsif ($key_commands =~ /,$key,/) {
		$text="";
		if ($value) {
		    if (-s $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'client'}.'/'.$value) {
			open U,$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'client'}.'/'.$value;
			while ($row=<U>) { $text .= $row; }
			close U;
			$in{$key} = $text;
			$in{$key} =~ s/\r+//g;
		    } else {
			delete($in{$key});
		    }
		}
	    } elsif ($key_key =~ /,$key,/) {
		$in{$key} = 1;
	    } elsif ($key_skip =~ /,$key,/) {
		next;
	    } else {
		$in{'adds_conf'} .= $row."\n";
	    }
	}
    }
    if (-s $config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'vpn'}.'/ccd/'.$in{'client'}) {
	open U,$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'vpn'}.'/ccd/'.$in{'client'};
	while ($row=<U>) { $text .= $row; }
	close U;
	$in{'ccdfile'} = $text;
	$in{'ccdfile'} =~ s/\r+//g;
    } else { $in{'ccdfile'} = ""; } 
    close F;
}

# Esegue il comando sparando su WEB i risultati mano a mano che arrivano. 
# Se il comando fallisce esce altrimenti ritorna 1
sub PrintCommandWEB {
    local ($cmd,$title,$ch,$i);
    $cmd =$_[0];
    $title = $_[1];
    print "<table border width=100%>\n";
    print "<tr $tb>";
    print "<td><b>".$title."</b></td>\n";
    print "</tr></table>";

    print "<pre>";
    # 2 printa a video STDOUT e STDERR
    &open_execute_command(CMD, $cmd, 2);
    $i = 0;
    while (read(CMD,$ch,1)) { 
	if ($ch eq "\n") { $i = 0; }
	if ($i == 100) { print "\n"; $i = 0; }
	print $ch; 
	$i++;
    }
    close(CMD);
    print "</pre>\n";
    if ($?) {
	print "<table border width=100%>\n";
        print "<tr $tb>";
        print "<td><b>".$title." ".$text{'failed'}."</b></td>\n";
        print "</tr></table>";
	return(0);
    } else {
	print "<table border width=100%>\n";
        print "<tr $tb>";
        print "<td><b>".$title." ".$text{'ok'}."</b></td>\n";
        print "</tr></table>";
	return(1);
    }
}

sub is_openvpn_running {
    local ($found_inet, @openvpnpids);
    @openvpnpids = &find_byname($config{'openvpn_path'});
    return(@openvpnpids); 
}
#devbr=Brücken-Device
#netdevbr=Netzwerkkarte für Bridge
#ifconfigbr=IP Konfiguration der Bridge
#ipbr=IP-Adresse/Gateway
#netmaskbr=Netzmaske
#iprangebr=IP-Range für Bridge-Clients
#iprangestartbr=Start
#iprangeendbr=Ende

sub bridge_control_elements{
	my $br_ctl_elements = '';
	$br_ctl_elements .= &ui_table_row($text{'devbr'},&ui_textbox('devbr',$in{'devbr'},4));
	$br_ctl_elements .= &ui_table_row($text{'netdevbr'},&ui_select('netdevbr',$in{'netdevbr'},$a_eth ));
	$br_ctl_elements .= &ui_table_row($text{'ifconfigbr'},$text{'ipbr'}.' :'.&ui_textbox('ipbr',$in{'ipbr'},15).'<br>'.$text{'netmaskbr'}.' :'.&ui_textbox('netmaskbr',$in{'netmaskbr'},15));
	$br_ctl_elements .= &ui_table_row($text{'iprangebr'},$text{'iprangestartbr'}.':'.&ui_textbox('iprangestart',$in{'iprangestart'},15).' '.$text{'iprangeendbr'}.':'.&ui_textbox('iprangeend',$in{'iprangeend'},15));
	return ($br_ctl_elements);
}

# ip or netmask check
# parameter: ip|netmask|network , ip-address | network-address | netmask-address
sub check_ip_netmask{
    my $check_type = shift;
    my $check_value = shift;
    my $result = "true";
    my $segm = 0;
    my @part = ();
    if ($check_value !~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/){
	$result =  "false";
    } elsif ($check_type =~ /ip/){
        @part = split(/\./,$check_value);
        foreach $p ( @part ) {
            $segm += 1;
            if ( (($segm == 1) || ($segm == 4)) && ($p < 1 or $p > 254)) {
                $result = "false";
                last;
            } elsif ($p < 0 or $p > 254){
                $result = "false";
                last;
            }
        }
    } elsif ($check_type =~ /network/){
        @part = split(/\./,$check_value);
        foreach $p ( @part ) {
            $segm += 1;
            if ( ($segm == 1) && ($p < 1 or $p > 254)) {
                $result = "false";
                last;
            } elsif ($p < 0 or $p > 254){
                $result = "false";
                last;
            }
       }
    } elsif ($check_type =~ /netmask/){
        @part = split(/\./,$check_value);
        foreach $p ( @part ) {
    	    if ($p < 0 or $p > 255) {
                $result = "false";
                last;
            }
        }
    }
    return($result)
}

1;
