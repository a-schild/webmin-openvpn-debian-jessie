#!/usr/bin/perl

#########################################################################
#   Autori:             Marco Colombo (marco@openit.it)
#                       Giuliano Natali Diaolin (diaolin@openit.it)
#   Copyright:          Open It S.r.l.
#                       Viale Dante, 78
#                       38057 Pergine Valsugana (TN) ITALY
#                       Tel: +39 0461 534800 Fax: +39 0461 538443
##############################################################################

use Time::Local;

require './openvpn-lib.pl';

# legge parametri da form o da url e li inserisce in hash $in
&ReadParse();

# legge info della CA: hash globale $info_ca
&ReadFieldsCA($in{'file_name'});

# legge elenco delle chiavi presenti per quella CA
$listca = &ReadCAKeys($in{'file_name'},0);

# intestazione pagina
&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

print "<BR>";
# start tabella
print "<table border width=100%>\n";
# title row
print "<tr $tb>";
    print "<td colspan=7 nowrap><b>".$text{'list_keys_of_ca'}." ".$in{'file_name'}."</b></td>\n";
print "</tr>\n";
# th row
print "<tr $tb>";
if (keys %{$listca}) {
    print "<td width='40%' nowrap><b>".$text{'name'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'key_server'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'verify'}."</b></td>\n";
    print "<td width='1%' colspan=2 align=center nowrap><b>".$text{'export'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'status'}."</b></td>\n";
    print "<td width='1%' nowrap><b>&nbsp;</b></td>\n";
} else {
    print "<td colspan=7 align=center nowrap><b>".$text{'list_keys_empty'}."</b></td>\n";
}
print "</tr>\n";
# rows
foreach $key (sort keys %{$listca}) {
    print "<tr $cb>\n";
	if ($$listca{$key}{key_expired} =~ /^\d{12}Z$/) {
    	    $$listca{$key}{key_expired} =~ /^(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)Z$/;
	    $time = Time::Local::timegm($6,$5,$4,$3,($2-1),"20".$1);	    
	} elsif ($$listca{$key}{key_expired} =~ /^\d{14}Z$/) {
	    $$listca{$key}{key_expired} =~ /^(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)Z$/;
	    $time = Time::Local::timegm($7,$5,$4,$3,($2-1),$1);
	}
	$mytime = time();
	print "<td nowrap><a href=\"view_key.cgi?ca_name=".$in{'file_name'}."&key_name=".$$listca{$key}{key_name}."&key_id=".$$listca{$key}{key_id}."\" title=\"".$text{'viewkey'}."\">".$$listca{$key}{key_name}."</a></td>\n";
	if (-f $$info_ca{'KEY_DIR'}.'/'.$in{'file_name'}.'/'.$$listca{$key}{key_name}.'.server') {
	    print "<td nowrap><strong>".$text{'server'}."</strong></td>\n";
	} else {
	    print "<td nowrap>".$text{'client'}."</td>\n";
	}
	print "<td nowrap><a href=\"verify_key.cgi?ca_name=".$in{'file_name'}."&key_name=".$$listca{$key}{key_name}."&key_id=".$$listca{$key}{key_id}."\" title=\"".$text{'verifykey'}."\">".$text{'verify'}."</a></td>\n";
	if ($$listca{$key}{key_status} eq "R" or $time < $mytime) {	
	    print "<td nowrap>&nbsp;</td>\n";
	    print "<td nowrap>&nbsp;</td>\n";
	} else {
	    print "<td nowrap><a href=\"export_key.cgi?type_key=1&ca_name=".$in{'file_name'}."&key_name=".$$listca{$key}{key_name}."&key_id=".$$listca{$key}{key_id}."\" title=\"".$text{'export_key'}."\">".$text{'export'}."</a></td>\n";
	    if (-s $$info_ca{'KEY_DIR'}.'/'.$in{'file_name'}.'/'.$$listca{$key}{key_name}.'.p12') {
		print "<td nowrap><a href=\"export_key.cgi?type_key=2&ca_name=".$in{'file_name'}."&key_name=".$$listca{$key}{key_name}."&key_id=".$$listca{$key}{key_id}."\" title=\"".$text{'export_pk12'}."\">".$text{'pkcs12'}."</a></td>\n";
	    } else {
		print "<td nowrap>&nbsp;</td>\n";
	    }
	}
	if ($$listca{$key}{key_status} eq "R") {
	    print "<td nowrap><span style=\"color:red\">".$text{'revoked'}."</span></td>\n";
	} elsif ($$listca{$key}{key_status} eq "V") {
	    if ($time < $mytime) {
		print "<td nowrap><span style=\"color:black;font-weight:bold;\">".$text{'expired'}."</span></td>\n";
	    } else {
		print "<td nowrap><span style=\"color:green\">".$text{'active'}."</span></td>\n";
	    }
	}
	print "<td nowrap><a href=\"remove_key.cgi?ca_name=".$in{'file_name'}."&key_name=".$$listca{$key}{key_name}."&key_id=".$$listca{$key}{key_id}."\" title=\"".$text{'removekey'}."\">".$text{'remove'}."</a></td>\n";
    print "</tr>\n";
}
# stop tabella
print "</table>\n";
print "<BR>";
print "<hr>\n";
print "<BR>";

# form per nuova Key
print &ui_form_start("create_key.cgi", "POST");
print &ui_hidden('ca_name', $in{'file_name'});
print &ui_hidden('KEY_DIR', $$info_ca{'KEY_DIR'}."/".$in{'file_name'});
print &ui_hidden('KEY_CONFIG', $$info_ca{'KEY_CONFIG'});
print &ui_hidden('KEY_SIZE', $$info_ca{'KEY_SIZE'});
print &ui_table_start($text{'newkey_title'}.": ".$in{'file_name'},'',2);
print &ui_table_row($text{'key_name'}, &ui_textbox('KEY_NAME','changeme',50),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'key_password'}, &ui_password('KEY_PASSWD','',50),'',[ 'nowrap',1 ]);
print &ui_table_row('','<strong>'.$text{'warning_server_pass'}.'</strong>',[ 'align=right colspan=2 nowrap',1 ]);
print &ui_table_row($text{'key_server'}, &ui_select('KEY_SERVER', 2, [ [2,$text{'client'}], [1,$text{'server'}] ]),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'key_pkcs12'}, &ui_select('KEY_PKCS12', 1, [ [1,$text{'no'}],[2,$text{'yes'}] ]),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'key_pkcs12_password'}, &ui_password('KEY_PKCS12_PASSWD','',50),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'key_expire'}, &ui_textbox('KEY_EXPIRE', $$info_ca{'CA_EXPIRE'},50),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'country'}, &ui_textbox('KEY_COUNTRY', $$info_ca{'KEY_COUNTRY'},50),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'province'}, &ui_textbox('KEY_PROVINCE', $$info_ca{'KEY_PROVINCE'},50),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'city'}, &ui_textbox('KEY_CITY', $$info_ca{'KEY_CITY'},50),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'org'}, &ui_textbox('KEY_ORG', $$info_ca{'KEY_ORG'},50),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'ou'}, &ui_textbox('KEY_OU', 'Office',50),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'email'}, &ui_textbox('KEY_EMAIL', $$info_ca{'KEY_EMAIL'},50),'',[ 'nowrap',1 ]);
print &ui_table_end();
print &ui_form_end([ [ "save", $text{'save'} ] ]);

print "<BR>";

print "<hr>\n";
print "<BR>";

#footer della pagina
&footer("", $text{'title_opnvpn'});
