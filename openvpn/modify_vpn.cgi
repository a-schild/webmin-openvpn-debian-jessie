#!/usr/bin/perl

#########################################################################
#   Autori:             Marco Colombo (marco@openit.it)
#                       Giuliano Natali Diaolin (diaolin@openit.it)
#   Copyright:          Open It S.r.l.
#                       Viale Dante, 78
#                       38057 Pergine Valsugana (TN) ITALY
#                       Tel: +39 0461 534800 Fax: +39 0461 538443
##############################################################################

require './openvpn-lib.pl';

# legge parametri da form o da url e li inserisce in hash $in
&ReadParse();

&ReadVPNConf();

&ReadFieldsCA($in{'ca'});

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

# array derivante da comando 'openvpn --show-ciphers': il valore e' il primo campo ed etichetta tutto
$a_cypher = &ReadCiphers();
#$a_cypher = [];
#&open_execute_command(CMD, $config{'openvpn_path'} . ' --show-ciphers', 2);
#while ($row=<CMD>) {
#    $row =~ s/\r*\n//g;
#    if (($row =~ /bit default key/i) or ($row =~ /bit key,/i) or ($row =~ /bit key by default,/i)) {
#	($key) = split(' ',$row);
#	push(@$a_cypher,[$key,$row]);	
#    }
#}
#close(CMD);

#array of aviable ethernet devices
$a_eth = &ReadEths($in{'devbr'});
#$a_eth = [];
#&open_execute_command(CMD, 'ifconfig|grep -i :ethernet |awk \'{print $1}\'', 2);
#while ($row=<CMD>) {
#	$row =~ s/\r*\n//g;
#	if (($row ne $in{'devbr'}) && (($row !~ /^tap\d/))) {
#		push(@$a_eth,[$row,$row]);
#	}
#}
#close(CMD);

# estrarre elenco chiavi server [della ca selezionata]
$a_server = &ReadCAKeys($in{'ca'},2,1);

# intestazione pagina
&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

print "<BR>";

if (!$in{'local'}) { $in{'local'} = "ALL"; }
if ($in{'dev'} =~ /^tap\d/) {  $in{'dev'} =~ s/^tap\d/tap/; }

# form per nuova VPN
print &ui_form_start("create_vpn.cgi", "POST");
print &ui_hidden('ca_dir',$config{'openvpn_keys_subdir'}.'/'.$in{'ca'});
print &ui_hidden('ca',$config{'openvpn_keys_subdir'}.'/'.$in{'ca'}.'/ca.crt');
print &ui_hidden('ca_name',$in{'ca'});
print &ui_hidden('VPN_NAME',$in{'vpn'});
if ($in{'tls-auth-old'}) {
    $in{'tls-auth-old'} =~ s/ 0$//; 
    print &ui_hidden('tls-auth-old',$in{'tls-auth-old'});
}
print &ui_hidden('port',$in{'port'});
print &ui_hidden('management_url','127.0.0.1');
print &ui_hidden('modify',1);
print &ui_hidden('ccd-exclusive',1);
print &ui_hidden('dh',$config{'openvpn_keys_subdir'}.'/'.$in{'ca'}.'/dh'.$$info_ca{'KEY_SIZE'}.'.pem');
print &ui_hidden('crl-verify',$config{'openvpn_keys_subdir'}.'/'.$in{'ca'}.'/crl.pem');
print &ui_table_start($text{'modifyvpn_server_title'},'',2);
print &ui_table_row($text{'name'}, $in{'vpn'});
print &ui_table_row($text{'port'}, $in{'port'});
print &ui_table_row($text{'protocol'}, &ui_select('proto', $in{'proto'}, [ ['udp','udp'],['tcp-server','tcp-server'],['tcp-client','tcp-client'] ]));
$in{'dev'} =~ /^(\D*)(\d*)$/;
$dev = $1;
$numberdev = $2;
print &ui_table_row($text{'dev'}, &ui_hidden('dev',$in{'dev'}).$dev." ".&ui_textbox('numberdev', $numberdev, 3));
##############################
##############################
if ($dev eq 'tap') { print bridge_control_elements(); }
##############################
##############################
print &ui_table_row($text{'management'}, $text{'management_enable'}.': '.&ui_select('management', $in{'management'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]).' '.$text{'management_url'}.': 127.0.0.1 '.$text{'management_port'}.': '.&ui_textbox('management_port',$in{'management_port'},5));
print &ui_table_row($text{'ca'}, $in{'ca'});
if (@{$a_server}) { 
    print &ui_table_row($text{'choose_server'}, &ui_select('choose_server', $in{'choose_server'}, $a_server));
} else {
    print &ui_table_row($text{'choose_server'}, "<span style='color:red'>".$text{'list_keys_server_empty'}."</span>");
}
print &ui_table_row($text{'cert_server'}, $text{'automatic'});
print &ui_table_row($text{'key_server'}, $text{'automatic'});
print &ui_table_row($text{'dh'}, 'dh'.$$info_ca{'KEY_SIZE'}.'.pem');
print &ui_table_row($text{'tls-server'}, &ui_select('tls-server', $in{'tls-server'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
print &ui_table_row($text{'local'}, &ui_textbox('local',$in{'local'},50));
print &ui_table_row($text{'new_vpn_server'}, $text{'network'}.''.&ui_textbox('network',$in{'network'},15)." ".$text{'netmask'}.''.&ui_textbox('netmask',$in{'netmask'},15));
print &ui_table_row($text{'ifconfig-pool-persist'}, &ui_select('ifconfig-pool-persist', $in{'ifconfig-pool-persist'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
print &ui_table_row($text{'client-to-client'}, &ui_select('client-to-client', $in{'client-to-client'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
print &ui_table_row($text{'duplicate-cn'}, &ui_select('duplicate-cn', $in{'duplicate-cn'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
print &ui_table_row($text{'tls-auth'}, &ui_select('tls-auth', $in{'tls-auth'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
print &ui_table_row($text{'ccd-exclusive'}, $text{'yes'});
print &ui_table_row($text{'cipher'}, &ui_select('cipher', $in{'cipher'}, $a_cypher));
print &ui_table_row($text{'comp-lzo'}, &ui_select('comp-lzo', $in{'comp-lzo'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
print &ui_table_row($text{'max-clients'}, &ui_textbox('max-clients',$in{'max-clients'},4));
print &ui_table_row($text{'user'}, &ui_select('user', $in{'user'}, $a_user));
print &ui_table_row($text{'group'}, &ui_select('group', $in{'group'}, $a_group));
print &ui_table_row($text{'persist-key'}, &ui_select('persist-key', $in{'persist-key'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
print &ui_table_row($text{'persist-tun'}, &ui_select('persist-tun', $in{'persist-tun'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
print &ui_table_row($text{'keepalive'}, $text{'keepalive_ping'}.': '.&ui_textbox('keepalive_ping',$in{'keepalive_ping'},3)." ".$text{'keepalive_ping-restart'}.': '.&ui_textbox('keepalive_ping-restart',$in{'keepalive_ping-restart'},3));
print &ui_table_row($text{'verb'}, &ui_select('verb', $in{'verb'}, $a_verb));
print &ui_table_row($text{'mute'}, &ui_select('mute', $in{'mute'}, $a_mute));
print &ui_table_row($text{'status'}, 'openvpn-status.log');
print &ui_table_row($text{'log-append'}, 'openvpn.log');
print &ui_table_row($text{'tun-mtu'}, &ui_textbox('tun-mtu',$in{'tun-mtu'},4));
print &ui_table_row($text{'fragment'}, &ui_textbox('fragment',$in{'fragment'},4));
print &ui_table_row($text{'mssfix'}, &ui_textbox('mssfix',$in{'mssfix'},4));
print &ui_table_row($text{'float'}, &ui_select('float', $in{'float'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
print &ui_table_row($text{'chroot'}.' '.$config{'openvpn_home'}, &ui_select('chroot', $in{'chroot'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
print &ui_table_row($text{'topology'}, &ui_select('topology',$in{'topology'}, [ ['subnet','subnet'],['net30','net30'],['p2p','p2p'] ]));
print &ui_table_row($text{'adds_conf'}, &ui_textarea('adds_conf', $in{'adds_conf'}, 5,45,'off'));
print &ui_table_end();
print &ui_table_start($text{'commands'},'',2);
print &ui_table_row($text{'up-pre'}, &ui_textarea('up-pre', $in{'up-pre'}, 3, 45, 'off'));
print &ui_table_row($text{'up'}, &ui_textarea('up', $in{'up'}, 3, 45, 'off'));
print &ui_table_row($text{'down-pre'}, &ui_textarea('down-pre', $in{'down-pre'}, 3, 45, 'off'));
print &ui_table_row($text{'down'}, &ui_textarea('down', $in{'down'}, 3, 45, 'off'));
print &ui_table_row($text{'down-root'}, &ui_textarea('down-root', $in{'down-root'}, 3, 45, 'off'));
print &ui_table_end();
print &ui_form_end([ [ "save", $text{'save'} ] ]);

print "<BR><BR>";

#footer della pagina
&footer("listvpn.cgi", $text{'listserver_title'});
0
