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

&ReadFieldsCA($in{'file_name'});

# intestazione pagina
&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

print "<BR>";
if (keys %{$info_ca}) {
    print &ui_table_start($text{'viewca_title'},'',2);
    print &ui_table_row($text{'ca_ca_name'}, $$info_ca{'CA_NAME'},'',[ 'nowrap',1 ]);
    print &ui_table_row($text{'ca_key_config'}, $$info_ca{'KEY_CONFIG'},'',[ 'nowrap',1 ]);
    print &ui_table_row($text{'ca_key_dir'}, $$info_ca{'KEY_DIR'},'',[ 'nowrap',1 ]);
    print &ui_table_row($text{'ca_key_size'}, $$info_ca{'KEY_SIZE'},'',[ 'nowrap',1 ]);
    print &ui_table_row($text{'ca_ca_expire'}, $$info_ca{'CA_EXPIRE'},'',[ 'nowrap',1 ]);
    print &ui_table_row($text{'country'}, $$info_ca{'KEY_COUNTRY'},'',[ 'nowrap',1 ]);
    print &ui_table_row($text{'province'}, $$info_ca{'KEY_PROVINCE'},'',[ 'nowrap',1 ]);
    print &ui_table_row($text{'city'}, $$info_ca{'KEY_CITY'},'',[ 'nowrap',1 ]);
    print &ui_table_row($text{'org'}, $$info_ca{'KEY_ORG'},'',[ 'nowrap',1 ]);
    print &ui_table_row($text{'email'}, $$info_ca{'KEY_EMAIL'},'',[ 'nowrap',1 ])."\n";
    print &ui_table_end();
} else {
    # start tabella
    print "<table border width=100%>\n";
    # th row
    print "<tr $tb>";
    print "<td nowrap><b>".$text{'no_data_ca'}."</b></td>\n";
    print "</tr>\n";
    # stop tabella
    print "</table>\n";
}
print "<BR><BR>";

#footer della pagina
&footer("listca.cgi", $text{'listca_title'});
