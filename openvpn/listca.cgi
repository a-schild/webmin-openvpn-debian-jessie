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

$listca = &ReadCA();

# intestazione pagina
&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

print "<BR>";

# start tabella
print "<table border width=100%>\n";
# title row
print "<tr $tb>";
    print "<td colspan=5 nowrap><b>".$text{'listca_title'}."</b></td>\n";
print "</tr>\n";
# th row
print "<tr $tb>";
if (keys %{$listca}) {
    print "<td width='40%' nowrap><b>".$text{'name'}."</b></td>\n";
    print "<td><b>".$text{'notes'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'info'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'keyslist'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'remove'}."</b></td>\n";
} else {
    print "<td colspan=5 align=center nowrap><b>".$text{'list_ca_empty'}."</b></td>\n";
}
print "</tr>\n";
# rows
foreach $key (sort keys %{$listca}) {
    print "<tr $cb>\n";
	print "<td nowrap><a href=\"view_ca.cgi?file_name=".$$listca{$key}{ca_name}."\" title=\"".$text{'viewca'}."\">".$$listca{$key}{ca_name}."</a></td>\n";
	print "<td>".$$listca{$key}{ca_error}."</td>\n";
	print "<td nowrap><a href=\"verify_ca.cgi?file_name=".$$listca{$key}{ca_name}."\" title=\"".$text{'infoca'}."\">".$text{'infoca'}."</a></td>\n";
	print "<td nowrap><a href=\"keyslist_ca.cgi?file_name=".$$listca{$key}{ca_name}."\" title=\"".$text{'keyslistca'}."\">".$text{'keyslist'}."</a></td>\n";
	print "<td nowrap><a href=\"remove_ca.cgi?file_name=".$$listca{$key}{ca_name}."\" title=\"".$text{'removeca'}."\">".$text{'remove'}."</a></td>\n";
    print "</tr>\n";
}
# stop tabella
print "</table>\n";
print "<BR>";
print "<hr>\n";
print "<BR>";

# form per nuova CA
print &ui_form_start("create_ca.cgi", "POST");
print &ui_table_start($text{'newca_title'},'',2);
print &ui_table_row($text{'ca_ca_name'}, &ui_textbox('CA_NAME','changeme',50),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'ca_key_config'}, &ui_textbox('KEY_CONFIG',$config{'openssl_home'},50),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'ca_key_dir'}, $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'},'',[ 'nowrap',1 ]);
print &ui_table_row($text{'ca_key_size'}, &ui_select('KEY_SIZE', 2048, [ [2048,2048], [4096,4096] ]),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'ca_ca_expire'}, &ui_textbox('CA_EXPIRE', '3650',50),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'country'}, &ui_textbox('KEY_COUNTRY', 'US',50),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'province'}, &ui_textbox('KEY_PROVINCE', 'NY',50),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'city'}, &ui_textbox('KEY_CITY', 'New York',50),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'org'}, &ui_textbox('KEY_ORG', 'My Org',50),'',[ 'nowrap',1 ]);
print &ui_table_row($text{'email'}, &ui_textbox('KEY_EMAIL', 'me@my.org',50),'',[ 'nowrap',1 ]);
print &ui_table_end();
print &ui_form_end([ [ "save", $text{'save'} ] ]);
print "<BR>";
print "<hr>\n";
print "<BR>";

#footer della pagina
&footer("", $text{'title_opnvpn'});
