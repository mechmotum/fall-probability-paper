%% LaTeX class for TU Delft letter in Dutch and English
%% Version: 3.0
%% Author: Ronald Ligteringen
%% Date: 20160817
%% log:
%% v2.1: added CC with ifthen statement in closing
%% v3.0: added second signature
%% v3.1: change logo TU Delft (without descriptor)
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{tuletter}[2016/08/17 TU Delft letter class]

% The TU letter is defined for A4 and 10pt
\LoadClass[a4paper,10pt]{article}
% Font type Sans Serif
\renewcommand*{\familydefault}{\sfdefault}
% Paragraph without indention and with white line
\setlength{\textwidth}{136mm}
\setlength{\parindent}{0em}
\setlength{\parskip}{0.7em}

%\usepackage[absolute,showboxes]{textpos}
\RequirePackage[absolute]{textpos} % positioning the header elements
\RequirePackage[usenames,dvipsnames]{color} % use gray color for default values and labels
\RequirePackage{graphicx} % for logo
\RequirePackage{epstopdf} % converting logo for PDF
\RequirePackage{calc} % calculate lengths
\RequirePackage{geometry} % redefine margins
\RequirePackage{lastpage} % for pagecounter in footer
\RequirePackage{fancyhdr} % for pagecounter in footer
\RequirePackage{ifthen}
\RequirePackage{tabularx} % for two signatures

%%% Multilingual with translations
% First read option, set default to Dutch (nl)
% this can be extended with more languages
\newcommand\TL@lang{}
\DeclareOption{nl}{\renewcommand\TL@lang{nl}}
\DeclareOption{en}{\renewcommand\TL@lang{en}}
\ExecuteOptions{nl}
\ProcessOptions
% Load packages
\RequirePackage[dutch,english]{babel}
\RequirePackage{ifthen}
%% TeX function that generates the language commands.
\def\localedef#1#2{
\ifthenelse{ \equal{\locale}{#1} }{
  \selectlanguage{#2}
  \expandafter\def\csname#1\endcsname ##1{##1}
  }{
  \expandafter\def\csname#1\endcsname ##1{}
  }
}
%% Selected language. Can be placed anywhere before the language commands.
\providecommand\locale{\TL@lang}
%% Language commands.
\localedef{nl}{dutch}
\localedef{en}{english}
%%% end multilingual

% Font color for default values (values not defined in LaTeX file)
\newcommand{\tudefault}[1]{\textcolor{Gray}{#1}}

%%% Definition of user fields and default values
% Signature at the end of the letter
\newcommand\signimage[1]{\def\tusignimage{#1}}
\signimage{}
\newcommand\signname[1]{\def\tusignname{#1}}
\signname{\tudefault{your signature}}
% Second Signature at the end of the letter
\newcommand\signimagesec[1]{\def\tusignimagesec{#1}}
\signimagesec{}
\newcommand\signnamesec[1]{\def\tusignnamesec{#1}}
\signnamesec{}
% Reference top left
\renewcommand\date[1]{\def\tudate{#1}}
\date{\tudefault{\today}}
\newcommand\ourref[1]{\def\tuourref{#1}}
\ourref{\tudefault{our reference}}
\newcommand\yourref[1]{\def\tuyourref{#1}}
\yourref{\tudefault{your reference}}
\newcommand\contact[1]{\def\tucontact{#1}}
\contact{\tudefault{contact name}}
\newcommand\phone[1]{\def\tuphone{#1}}
\phone{\tudefault{+31 (0)15 278 \ldots}}
\newcommand\email[1]{\def\tuemail{#1}}
\email{\tudefault{\ldots @tudelft.nl}}
\newcommand\subject[1]{\def\tusubject{#1}}
\subject{\tudefault{subject}}
% Recipient left under reference
\newcommand\toname[1]{\def\tutoname{#1}}
\toname{\tudefault{recipient name}}
\newcommand\toaddress[1]{\def\tutoaddress{#1}}
\toaddress{\tudefault{recipient address}}
% Sender right under logo
\newcommand\fromname[1]{\def\tufromname{#1}}
\fromname{\tudefault{TU Delft}}
\newcommand\fromaddress[1]{\def\tufromaddress{#1}}
\fromaddress{\tudefault{\ldots\\2628 CJ Delft}}
\newcommand\frompobox[1]{\def\tufrompobox{#1}}
\frompobox{Postbus 5045\\2600 AA Delft}
% CC under signature
\newcommand\cc[1]{\def\tucc{#1}}
\cc{}
%%% end user fields

%%% header layout
\newcommand{\tumarginleft}{37mm}
\newcommand{\tumarginbottom}{20mm}
\geometry{left=\tumarginleft,bottom=\tumarginbottom}
% NOTE : This command doesn't result in this value being a number. So I changed
% it to the English value.
%\newcommand{\tumarginleftref}{\nl{16.5}\en{17.5}mm}
\newcommand{\tumarginleftref}{17.5mm}
\newcommand{\tumargintopref}{9mm}
\newcommand{\tumarginleftsender}{132mm}
\newcommand{\tumargintopsender}{59mm}
\newcommand{\tumargintoplogo}{\tumargintopref-5mm}
\newcommand{\tumarginleftlogo}{\tumarginleftsender-4.6mm}
\newcommand{\tumargintoprecip}{68mm}
%%% end header layout

%%% Labels
% Font size in Reference values
\newcommand{\turefval}[1]{\small{#1}}
% Font color and size in Reference labels
\newcommand{\tureflab}[1]{\textcolor{Gray}{\scriptsize{#1}}}
% Font size in Sender
\newcommand{\tusen}[1]{\normalsize{#1}}
% Reference labels
%\newcommand\tudatename{\nl{Datum}\en{Date}}
%\newcommand\tuourrefname{\nl{Ons kenmerk}\en{Our reference}}
%\newcommand\tuyourrefname{\nl{Uw kenmerk}\en{Your reference}}
%\newcommand\tucontactname{\nl{Contactpersoon}\en{Contact}}
%\newcommand\tuphonename{\nl{Telefoon}\en{Phone}}
%\newcommand\tuemailname{E-mail}
%\newcommand\tusubjectname{\nl{Onderwerp}\en{Subject}}
\newcommand\tudatename{Date}
\newcommand\tuourrefname{Our reference}
\newcommand\tuyourrefname{Your reference}
\newcommand\tucontactname{Contact}
\newcommand\tuphonename{Phone}
\newcommand\tuemailname{E-mail}
\newcommand\tusubjectname{Subject}
% Sender label
%\newcommand\tufrompoboxname{\nl{Correspondentie}\en{PO Box}}
\newcommand\tufrompoboxname{PO Box}
% CC label
%\newcommand\tuccname{\nl{Kopie}\en{CC}}
\newcommand\tuccname{CC}
% Page number label
%\newcommand\tupagenameprefix{\nl{Pag.}\en{Page}}
%\newcommand\tupagenamesuffix{\nl{van}\en{of}}
\newcommand\tupagenameprefix{Page}
\newcommand\tupagenamesuffix{of}
%%% end labels

%%% Page numbers in footer
\fancyhead{}
\fancyfoot{}
\rfoot{\small\tupagenameprefix~\thepage{}~\tupagenamesuffix~\pageref{LastPage}}
\pagestyle{fancy}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
%%% end footer

%%% This is the actual header of the letter
\newcommand{\makeheader}{%
% set origin for textblock
\textblockorigin{0cm}{0cm}

% Fold marks
%   on half
\begin{textblock*}{4mm}(4mm,148mm)
\rule{\hsize}{0.1pt}
\end{textblock*}
%   on one third
\begin{textblock*}{2mm}(4mm,98.3mm)
\rule{\hsize}{0.1pt}
\end{textblock*}
%   on two third
\begin{textblock*}{2mm}(4mm,196.7mm)
\rule{\hsize}{0.1pt}
\end{textblock*}

% Reference
\begin{textblock*}{100mm}(\tumarginleftref,\tumargintopref)
\begin{tabular}{r@{ }l}
  \tureflab{\tudatename} & \turefval{\tudate} \\
  \tureflab{\tuourrefname} & \turefval{\tuourref} \\
  \tureflab{\tuyourrefname} & \turefval{\tuyourref} \\
  \tureflab{\tucontactname} & \turefval{\tucontact} \\
  \tureflab{\tuphonename} & \turefval{\tuphone} \\
  \tureflab{\tuemailname} & \turefval{\tuemail} \\
  \tureflab{\tusubjectname} & \turefval{\tusubject} \\
\end{tabular}
\end{textblock*}

% Logo
\begin{textblock*}{8cm}(\tumarginleftlogo,\tumargintoplogo)
%% v3.1 as requested by TU the logo without descriptor is now used
% \includegraphics[height=3.7cm]{tudelft_logo_with_descr} % Logo with descriptor
\includegraphics[height=3.7cm]{tudelft_logo_without_descr} % Logo without desciptor
\end{textblock*}

% Sender
\begin{textblock*}{70mm}(\tumarginleftsender,\tumargintopsender)
\tusen{
{\bf\tufromname}\\
\\
\\
\tufromaddress\\
\\
\tureflab{\tufrompoboxname}\\
\tufrompobox
}
\end{textblock*}

% Recipient
\begin{textblock*}{75mm}(\tumarginleft,\tumargintoprecip)
\tutoname\\
\tutoaddress
\end{textblock*}
}
%%% end of header

%%% opening of letter
\newcommand{\opening}[1]{%
\vspace*{68mm}
#1\par\nobreak
\vspace{2\parskip}
}
%%% end of opening

%%% closing op letter
\newcommand{\closing}[1]{%
\par
\vspace{2\parskip}
#1\par\nobreak
\renewcommand{\tabcolsep}{0em}
\begin{tabularx}{\textwidth}{X X}
\ifthenelse{\equal{\tusignimage}{}}{\vspace{6\parskip}\nobreak}{\includegraphics[width=0.5\textwidth,height=25mm,keepaspectratio]{\tusignimage}\par\nobreak}
\tusignname &
\ifthenelse{\equal{\tusignimagesec}{}}{\vspace{6\parskip}\nobreak}{\includegraphics[width=0.5\textwidth,height=25mm,keepaspectratio]{\tusignimagesec}\par\nobreak}
\tusignnamesec \\
\end{tabularx}\par\nobreak
\ifthenelse{\equal{\tucc}{}}{}{\vspace{2\parskip}\tuccname: \tucc\nobreak}
}
%%% end of closing

\endinput
