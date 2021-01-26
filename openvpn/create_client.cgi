#!/usr/bin/perl

#########################################################################
#   Autori:             Marco Colombo (marco@openit.it)
#                       Giuliano Natali Diaolin (diaolin@openit.it)
#   Copyright:          Open It S.r.l.
#                       Viale Dante, 78
#                       38057 Pergine Valsugana (TN) ITALY
#                       Tel: +39 0461 534800 Fax: +39 0461 538443
##############################################################################

use File::Copy;

require './openvpn-lib.pl';

# legge parametri da form o da url e li inserisce in hash $in
&ReadParse();

$error = "";

# Controlli parametri form
if (!-d $config{'openvpn_home'}.'/'.$in{'ca_dir'} or !-s $config{'openvpn_home'}.'/'.$in{'ca_dir'}.'/ca.key' or !-s $config{'openvpn_home'}.'/'.$in{'ca_dir'}.'/ca.crt' or !-s $config{'openvpn_home'}.'/'.$in{'ca_dir'}.'/'.$in{'dh'}) {
    $error .= $text{'error_not_ca'}.'<BR>';
}

if (($in{'CLIENT_NAME'} !~ /^[a-zA-Z0-9_\-\.]{4,}$/) or ($in{'CLIENT_NAME'} =~ /\.{2,}/) or ($in{'CLIENT_NAME'} =~ /\.$/)){
    $error .= $text{'error_client_notok'}.' $&<BR>';
} elsif (-s $config{'openvpn_home'}.'/'.$in{'VPN_NAME'}.'.conf' and $in{'modify'} != 1) {
    $error .= $text{'error_client_exist'}.'<BR>';
}

if ($in{'remote_url'} !~ /\S/) {
    $error .= $text{'error_remote_url'}.'<BR>';
}

if ($in{'keepalive_ping'} and $in{'keepalive_ping-restart'}) {
    if ($in{'keepalive_ping'} =~ /\D/) {
	$error .= $text{'error_keepalive_ping'}.'<BR>';
    }
    if ($in{'keepalive_ping-restart'} =~ /\D/) {
	$error .= $text{'error_keepalive_ping-restart'}.'<BR>';
    }
}

if ($in{'adds_conf'}) { $in{'adds_conf'} =~ s/\r+//g; }

foreach $k (qw/fragment mssfix tun-mtu/) {
    if ($in{$k} and ($in{$k} < 100 or $in{$k} > 1500)) {
	$error .= $k.': '.$text{'error_mtu'}.'<BR>';
    }
}

$in{'choose_client'} = $in{'CLIENT_NAME'};

if (-s $config{'openvpn_home'}.'/'.$in{'ca_dir'}.'/'.$in{'choose_client'}.'.key' and -s $config{'openvpn_home'}.'/'.$in{'ca_dir'}.'/'.$in{'choose_client'}.'.crt') {
    # composti da choose_server
    $in{'key'} = $in{'choose_client'}.'.key';
    $in{'cert'} = $in{'choose_client'}.'.crt';
} else {
    $error .= $text{'error_choose_client'}.'<BR>';
}

if (!-d $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}) {
    mkdir($config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'},0700);
}
if ($in{'modify'} != 1) {
    # rimuovo directory se esistente
    if (-d $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'CLIENT_NAME'}) {
	&system_logged("rm -rf ".$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'CLIENT_NAME'}." >/dev/null 2>&1 </dev/null");
    }
    # crea le directory per il server
    mkdir($config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'CLIENT_NAME'},0700);
}

# chiavi per comandi attivazione/disattivazione
foreach $k (qw/up down up-pre down-pre/) {
    if ($in{'modify'}) {
	if (-f $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'CLIENT_NAME'}.'/'.$in{'CLIENT_NAME'}.'.'.$k) { unlink($config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'CLIENT_NAME'}.'/'.$in{'CLIENT_NAME'}.'.'.$k); }
    }
    if ($in{$k}) {
	$in{$k} =~ s/\r+//g;
	open U,">".$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'CLIENT_NAME'}.'/'.$in{'CLIENT_NAME'}.'.'.$k;
	print U $in{$k};
	close U;
	chmod(0700,$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'CLIENT_NAME'}.'/'.$in{'CLIENT_NAME'}.'.'.$k);
    }
}

%client_info = %in;
%in = ( 'vpn' => $client_info{'vpn'});
&ReadVPNConf();
%server_info = %in;
%in = %client_info;

# rieseguo la schermata di new con i campi riempiti dai valori inseriti 
# ed il messaggio di errore
if ($error) {
    
    if ($in{'modify'} != 1) {
	# rimuovo directory se esistente
	if (-d $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'CLIENT_NAME'}) {
	    &system_logged("rm -rf ".$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'CLIENT_NAME'}." >/dev/null 2>&1 </dev/null");
	}
    }

    &ReadFieldsCA($in{'ca_name'});

    $a_verb = [];
    for ($i=1;$i<=15;$i++) { push(@$a_verb,[$i,$i]); }

    $a_mute = [ [ 0, $text{'unassigned'} ] ];
    for ($i=10;$i<=50;$i=$i+10) { push(@$a_mute,[$i,$i]); }

    &foreign_require("useradmin", "user-lib.pl");

    # utenti di sistema
    $a_user = [];
    @users = &useradmin::list_users();
    @users = &useradmin::sort_users(\@users, 1);
    foreach $us (@users) {
	push @$a_user,[$$us{'user'},$$us{'user'}];
    }

    # gruppi di sistema
    $a_group = [];
    @groups = &useradmin::list_groups();
    @groups = &useradmin::sort_groups(\@groups, 1);
    foreach $us (@groups) {
	push @$a_group,[$$us{'group'},$$us{'group'}];
    }

    # estrarre elenco chiavi client [della ca selezionata]
    $a_clients = &ReadCAKeys($in{'ca_name'},3,1,1);

    # intestazione pagina
    &ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

    print "<BR>";
    print '<P><SPAN STYLE="color:red">'.$error.'</SPAN></P>';
    print "<BR>";

    if ($in{'proto'} eq "tcp-server") { $in{'proto'} = "tcp-client"; }

    # form per nuova VPN
    print &ui_form_start("create_client.cgi", "POST");
    print &ui_hidden('ca_dir',$config{'openvpn_keys_subdir'}.'/'.$$info_ca{'CA_NAME'});
    print &ui_hidden('ca','ca.crt');
    print &ui_hidden('ca_name',$$info_ca{'CA_NAME'});
    print &ui_hidden('vpn',$in{'vpn'});
    print &ui_hidden('tun-mtu',$in{'tun-mtu'});
    print &ui_hidden('dev',$in{'dev'});
    print &ui_hidden('mssfix',$in{'mssfix'});
    print &ui_hidden('proto',$in{'proto'});
    print &ui_hidden('remote_port',$in{'remote_port'});
    print &ui_hidden('cipher',$in{'cipher'});
    print &ui_hidden('modify',$in{'modify'});
    print &ui_hidden('tls-auth',$server_info{'tls-auth'});
    #print &ui_hidden('dev',$server_info{'dev'});
    if ($in{'modify'} == 1) {
	print &ui_hidden('CLIENT_NAME',$in{'CLIENT_NAME'});
        print &ui_table_start($text{'modifyclient_server_title'}.' '.$in{'vpn'},'',2);
	print &ui_table_row($text{'name'}, $in{'CLIENT_NAME'});
    } else {
        print &ui_table_start($text{'new_client_title'}.' '.$in{'vpn'},'',2);
	print &ui_table_row($text{'name'}, &ui_select('CLIENT_NAME', $in{'CLIENT_NAME'}, $a_clients));
    }
    print &ui_table_row($text{'protocol'}, $in{'proto'});
    print &ui_table_row($text{'dev'}, $in{'dev'});
    print &ui_table_row($text{'ca'}, $$info_ca{'CA_NAME'});
    print &ui_table_row($text{'choose_client'}, $text{'automatic_name'});
    print &ui_table_row($text{'cert_client'}, $text{'automatic'});
    print &ui_table_row($text{'key_client'}, $text{'automatic'});
    print &ui_table_row($text{'remote'}, $text{'remote_url'}.': '.&ui_textbox('remote_url',$in{'remote_url'},12).' '.$text{'remote_port'}.': '.$in{'remote_port'});
    if ($server_info{'tls-auth'} == 1) {
	print &ui_table_row($text{'tls-auth'}, $text{'yes'}." ".$text{'automatic_server'});
    } else {
	print &ui_table_row($text{'tls-auth'}, $text{'no'}." ".$text{'automatic_server'}); 
	}
    print &ui_table_row($text{'cipher'}, $in{'cipher'}." ".$text{'automatic_server'});
    print &ui_table_row($text{'comp-lzo'}, &ui_select('comp-lzo', $in{'comp-lzo'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'user'}, &ui_select('user', $in{'user'}, $a_user));
    print &ui_table_row($text{'group'}, &ui_select('group', $in{'group'}, $a_group));
    print &ui_table_row($text{'persist-key'}, &ui_select('persist-key', $in{'persist-key'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'persist-tun'}, &ui_select('persist-tun', $in{'persist-tun'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'keepalive'}, $text{'keepalive_ping'}.': '.&ui_textbox('keepalive_ping',$in{'keepalive_ping'},3)." ".$text{'keepalive_ping-restart'}.': '.&ui_textbox('keepalive_ping-restart',$in{'keepalive_ping-restart'},3));
    print &ui_table_row($text{'verb'}, &ui_select('verb', $in{'verb'}, $a_verb));
    print &ui_table_row($text{'mute'}, &ui_select('mute', $in{'mute'}, $a_mute));
    print &ui_table_row($text{'tun-mtu'}, $in{'tun-mtu'}." ".$text{'automatic_server'});
    print &ui_table_row($text{'fragment'}, &ui_textbox('fragment',$in{'fragment'},4));
    print &ui_table_row($text{'mssfix'}, $in{'mssfix'}." ".$text{'automatic_server'});
    print &ui_table_row($text{'float'}, &ui_select('float', $in{'float'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'auth-nocache'}, &ui_select('auth-nocache', $in{'auth-nocache'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'adds_conf'}, &ui_textarea('adds_conf', $in{'adds_conf'}, 5, 45, 'off'));
    print &ui_table_end();
    print &ui_table_start($text{'commands'},'',2);
    print &ui_table_row($text{'up-pre'}, &ui_textarea('up-pre', $in{'up-pre'}, 3, 45, 'off'));
    print &ui_table_row($text{'up'}, &ui_textarea('up', $in{'up'}, 3, 45, 'off'));
    print &ui_table_row($text{'down-pre'}, &ui_textarea('down-pre', $in{'down-pre'}, 3, 45, 'off'));
    print &ui_table_row($text{'down'}, &ui_textarea('down', $in{'down'}, 3, 45, 'off'));
    print &ui_table_end();
    print &ui_table_start($text{'ccdfile'},'',2);
    print &ui_table_row($text{'ccdfile-content'}, &ui_textarea('ccdfile', '', 3, 45, 'off'));
    print &ui_table_end();
    print &ui_form_end([ [ "save", $text{'save'} ] ]);

    print "<BR><BR>";

    #footer della pagina
    &footer("clientlist_vpn.cgi?vpn=".$in{'vpn'}, $text{'list_client_vpn'}." ".$in{'vpn'});

} else {

    # crea il file ta.key per la CA, se non esiste
    if ($in{'tls-auth'} == 1) {
	$in{'tls-auth'} = 'ta.key 1';
    } else {
	delete($in{'tls-auth'});
    }

    $in{'remote'} = $in{'remote_url'}.' '.$in{'remote_port'};

    if ($in{'modify'} == 1) {
	if (-s $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'CLIENT_NAME'}.'/'.$in{'CLIENT_NAME'}.'.conf') {
	    $namefile = $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'CLIENT_NAME'}.'/'.$in{'CLIENT_NAME'}.'.conf';
	} elsif (-s $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'CLIENT_NAME'}.'/'.$in{'CLIENT_NAME'}.'.disabled') {
    	    $namefile = $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'CLIENT_NAME'}.'/'.$in{'CLIENT_NAME'}.'.disabled';
	}
	open OUT, ">".$namefile;
	open CCD,">".$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'vpn'}.'/ccd/'.$in{'CLIENT_NAME'};
	print CCD $in{'ccdfile'};
	close CCD;
    } else {
	open CCD,">".$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'vpn'}.'/ccd/'.$in{'CLIENT_NAME'};
	print CCD $in{'ccdfile'};
	close CCD;
	chmod(0644,$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'vpn'}.'/ccd/'.$in{'CLIENT_NAME'});
	# scrivo file di configurazione client
	open OUT,">".$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'CLIENT_NAME'}.'/'.$in{'CLIENT_NAME'}.".conf";
    }
    open WCLI,">".$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'CLIENT_NAME'}.'/'.$in{'CLIENT_NAME'}.".ovpn";

    print OUT "client\n";
    print WCLI "client\r\n";

    if($in{proto} eq "tcp-server" or $in{proto} eq "tcp-client") {
       print OUT "proto tcp\n";
       print WCLI "proto tcp\r\n";
    } else {
       print OUT "proto".' '.$in{proto}."\n";
       print WCLI "proto".' '.$in{proto}."\r\n";
    }

    foreach $k (qw/dev ca cert key remote/) {
        print OUT $k.' '.$in{$k}."\n";
        print WCLI $k.' '.$in{$k}."\r\n";
    }

    foreach $k (qw/tls-auth cipher user group verb mute/) {
	if (exists($in{$k})) { 
	    print OUT $k.' '.$in{$k}."\n"; 
	    if ($k ne "user" and $k ne "group") { print WCLI $k.' '.$in{$k}."\r\n"; }
	}
    }

    foreach $k (qw/tun-mtu fragment mssfix/) {
        if ($in{$k} and exists($in{$k})) { 
	    print OUT $k.' '.$in{$k}."\n"; 
	    print WCLI $k.' '.$in{$k}."\r\n"; 
	}
    }

    if ($in{'keepalive_ping'} and $in{'keepalive_ping-restart'}) { 
	print OUT 'keepalive '.$in{'keepalive_ping'}.' '.$in{'keepalive_ping-restart'}."\n"; 
	print WCLI 'keepalive '.$in{'keepalive_ping'}.' '.$in{'keepalive_ping-restart'}."\r\n"; 
    }

    # se 1 allora scrivo solo la chiave altrimenti non la scrivo
    foreach $k (qw/comp-lzo persist-key persist-tun float auth-nocache/) {
	if ($in{$k} == 1) { 
	    print OUT $k."\n"; 
	    print WCLI $k."\r\n"; 
	}
    }


    print OUT "resolv-retry infinite\n";
    print WCLI "resolv-retry infinite\r\n";

    print OUT "nobind\n";
    print WCLI "nobind\r\n";
			   
    # chiavi per comandi attivazione/disattivazione
    foreach $k (qw/up down up-pre down-pre/) {
	if ($in{$k}) { 
	    print OUT $k.' '.$in{'CLIENT_NAME'}.'.'.$k."\n"; 
	    print WCLI $k.' '.$in{'CLIENT_NAME'}.'.'.$k."\r\n"; 
	}
    }

    if ($in{'adds_conf'}) { 
	print OUT $in{'adds_conf'}."\n"; 
	print WCLI $in{'adds_conf'}."\r\n"; 
    }

    close OUT;
    close WCLI;

    &redirect("clientlist_vpn.cgi?vpn=".$in{'vpn'});
}
