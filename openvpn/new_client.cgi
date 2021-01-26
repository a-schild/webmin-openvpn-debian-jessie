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

# estrarre elenco chiavi client [della ca selezionata]
$a_clients = &ReadCAKeys($in{'ca'},3,1,1,$in{'vpn'});

if ($in{'proto'} eq "tcp-server") { $in{'proto'} = "tcp-client"; }

# intestazione pagina
&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

print "<BR>";

if ($in{'dev'} =~ /\d/) { $in{'dev'} =~ s/\d+//; }

if (@$a_clients) {
    if ($in{'dev'} =~ /^tap\d+$/) { $in{'dev'} = 'tap'; }
    # form per nuova VPN
    print &ui_form_start("create_client.cgi", "POST");
    print &ui_hidden('ca_dir',$config{'openvpn_keys_subdir'}.'/'.$$info_ca{'CA_NAME'});
    print &ui_hidden('ca','ca.crt');
    print &ui_hidden('ca_name',$$info_ca{'CA_NAME'});
    print &ui_hidden('vpn',$in{'vpn'});	
    print &ui_hidden('tun-mtu',$in{'tun-mtu'});
    print &ui_hidden('mssfix',$in{'mssfix'});
    print &ui_hidden('proto',$in{'proto'});
    print &ui_hidden('dev',$in{'dev'});
    print &ui_hidden('remote_port',$in{'port'});
    print &ui_hidden('cipher',$in{'cipher'});
    print &ui_hidden('dh','dh'.$$info_ca{'KEY_SIZE'}.'.pem');
    print &ui_hidden('tls-auth',$in{'tls-auth'});
    print &ui_table_start($text{'new_client_title'}.' '.$in{'vpn'},'',2);
    print &ui_table_row($text{'name'}, &ui_select('CLIENT_NAME', '', $a_clients));
    print &ui_table_row($text{'protocol'}, $in{'proto'});
    print &ui_table_row($text{'dev'}, $in{'dev'});
    print &ui_table_row($text{'ca'}, $$info_ca{'CA_NAME'});
    print &ui_table_row($text{'choose_client'}, $text{'automatic_name'});
    print &ui_table_row($text{'cert_client'}, $text{'automatic'});
    print &ui_table_row($text{'key_client'}, $text{'automatic'});
    print &ui_table_row($text{'dh'}, 'dh'.$$info_ca{'KEY_SIZE'}.'.pem');
    print &ui_table_row($text{'remote'}, $text{'remote_url'}.': '.&ui_textbox('remote_url',$config{'default_server'},12).' '.$text{'remote_port'}.': '.$in{'port'});
    if ($in{'tls-auth'} == 1) {
	print &ui_table_row($text{'tls-auth'}, $text{'yes'}." ".$text{'automatic_server'});
    } else {
	print &ui_table_row($text{'tls-auth'}, $text{'no'}." ".$text{'automatic_server'});
    }
    print &ui_table_row($text{'cipher'}, $in{'cipher'}." ".$text{'automatic_server'});
    print &ui_table_row($text{'comp-lzo'}, &ui_select('comp-lzo', '1', [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'user'}, &ui_select('user', $in{'user'}, $a_user));
    print &ui_table_row($text{'group'}, &ui_select('group', $in{'group'}, $a_group));
    print &ui_table_row($text{'persist-key'}, &ui_select('persist-key', '1', [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'persist-tun'}, &ui_select('persist-tun', '1', [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'keepalive'}, $text{'keepalive_ping'}.': '.&ui_textbox('keepalive_ping','10',3)." ".$text{'keepalive_ping-restart'}.': '.&ui_textbox('keepalive_ping-restart','120',3));
    print &ui_table_row($text{'verb'}, &ui_select('verb', '2', $a_verb));
    print &ui_table_row($text{'mute'}, &ui_select('mute', '20', $a_mute));
    print &ui_table_row($text{'tun-mtu'}, $in{'tun-mtu'}." ".$text{'automatic_server'});
    print &ui_table_row($text{'fragment'}, &ui_textbox('fragment','',4));
    print &ui_table_row($text{'mssfix'}, $in{'mssfix'}." ".$text{'automatic_server'});
    print &ui_table_row($text{'float'}, &ui_select('float', 1, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'adds_conf'}, &ui_textarea('adds_conf', '', 5, 45, 'off'));
    print &ui_table_end();
    print &ui_table_start($text{'commands'},'',2);
    print &ui_table_row($text{'up-pre'}, &ui_textarea('up-pre', '', 3, 45, 'off'));
    print &ui_table_row($text{'up'}, &ui_textarea('up', '', 3, 45, 'off'));
    print &ui_table_row($text{'down-pre'}, &ui_textarea('down-pre', '', 3, 45, 'off'));
    print &ui_table_row($text{'down'}, &ui_textarea('down', '', 3, 45, 'off'));
    print &ui_table_end();
    print &ui_table_start($text{'ccdfile'},'',2);
    print &ui_table_row($text{'ccdfile-content'}, &ui_textarea('ccdfile', '', 3, 45, 'off'));
    print &ui_table_end();
    print &ui_form_end([ [ "save", $text{'save'} ] ]);
} else {
   # start tabella
    print "<table border width=100%>\n";
    # title row
    print "<tr $tb>";
        print "<td nowrap><b>".$text{'list_keys_client_empty'}."</b></td>\n";
    print "</tr>\n";
    print "</table>\n";
}

print "<BR><BR>";

#footer della pagina
&footer("clientlist_vpn.cgi?vpn=".$in{'vpn'}, $text{'list_client_vpn'}." ".$in{'vpn'});
