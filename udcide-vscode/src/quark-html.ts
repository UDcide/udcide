import { ThemeColor } from "vscode";
import { outputChannel } from "./constants";

/**
 * Generate WebView HTML for quark report.
 * @param report The data of quark report.
 * @returns WebView HTML
 */
export function quarkSummaryReportHTML(report: { [key: string]: any }): string {
    let allCrimesHTML = "";

    for (const key in report) {
        const crimeObj = report[key];
        allCrimesHTML += `
        <tr class="body" onclick="checkBoxClick(this.id)" id="${key}">
            <td class="column0"><input type="checkbox" name="rebuild-check" value="${crimeObj["crime"]}"></td>
            <td class="column1">${crimeObj["crime"]}</td>
            <td class="column2">${crimeObj["confidence"]}</td>
        </tr>`;

    }
    const backgroundColor = new ThemeColor("badge.background");
    const style = `

        .vscode-light body{
            background: ${backgroundColor};
            color: #e2e2e2;
        }
        .vscode-dark body{
            background: ${backgroundColor};
            color: #000;
        }

        .container-table100 {
            display: -webkit-box;
            display: -webkit-flex;
            display: -moz-box;
            display: -ms-flexbox;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;
            padding: 33px 30px;
        }

        .wrap-table100 {
            width: 100%;
        }

        table {
            table-layout: fixed;
            width: 100%;
        }

        th, td {
            font-weight: bold;
            padding-right: 10px;
        }

        .column0 {
            width: 5%;
            padding-left: 10px;
        }

        .column1 {
            width: 85%;
        }

        .column2 {
            width: 10%;
        }

        .table100-body td {
            padding-top: 16px;
            padding-bottom: 16px;
        }

        .table100 {
            position: relative;
            padding-top: 60px;
        }

        .table100-head {
            position: absolute;
            width: 100%;
            top: 0;
            left: 0;
        }

        .table100-body {
            max-height: 100%;
            overflow: auto;
        }

        .table100.ver5 .table100-head {
            padding-right: 30px;
        }

        .table100.ver5 th {
            text-align: left;
            font-family: Lato-Bold;
            font-size: 16px;
            line-height: 1.4;

            background-color: transparent;
        }

        .vscode-light .table100.ver5 td {
            font-family: Lato-Regular;
            font-size: 15px;
            line-height: 1.4;
            background-color: #d4d4d4;
        }

        .vscode-dark .table100.ver5 td {
            font-family: Lato-Regular;
            font-size: 15px;
            line-height: 1.4;
            background-color: #565656;
        }

        .vscode-light .table100.ver5 td.sub {
            font-family: Lato-Regular;
            font-size: 15px;
            line-height: 1.4;
            padding-left: 40px;
            background-color: #dcfddc;
        }

        .vscode-dark .table100.ver5 td.sub {
            font-family: Lato-Regular;
            font-size: 15px;
            line-height: 1.4;
            padding-left: 40px;
            background-color: #2f5658;
        }

        .table100.ver5 .table100-body tr {
            border-radius: 10px;
        }

        .table100.ver5 .table100-body table {
            border-collapse: separate;
            border-spacing: 0 10px;
        }

        .table100.ver5 .table100-body td {
            border: solid 1px transparent;
            border-style: solid none;
            padding-top: 10px;
            padding-bottom: 10px;
        }

        .table100.ver5 .table100-body td:first-child {
            border-left-style: solid;
            border-top-left-radius: 10px;
            border-bottom-left-radius: 10px;
        }

        .table100.ver5 .table100-body td:last-child {
            border-right-style: solid;
            border-bottom-right-radius: 10px;
            border-top-right-radius: 10px;
        }

        .vscode-light .table100.ver5 tr:hover td {
            background-color: #6b6b6b;
            cursor: pointer;
        }

        .vscode-dark .table100.ver5 tr:hover td {
            background-color: #000;
            cursor: pointer;
        }

        .vscode-light .table100.ver5 tr:hover td.sub {
            background-color: #90a790;
            cursor: pointer;
        }

        .vscode-dark .table100.ver5 tr:hover td.sub {
            background-color: #193435;
            cursor: pointer;
        }

        .table100.ver5 .table100-head th {
            padding-top: 25px;
            padding-bottom: 25px;
        }

        .api {
            padding-left: 50px;
        }

        .vscode-light .api a{
            color: #d05345;
        }

        .vscode-dark .api a{
            color: #ff9696;
        }

        .rebuild-btn {
            margin-top: 15px;
            background: none;
            border: 1px solid rgb(0, 196, 104);
            color: rgb(0, 196, 104);
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            border-radius: 10px;
            cursor: pointer;
        }

        .rebuild-btn:hover {
            background-color: rgb(0, 97, 52);
            border: 1px solid rgb(0, 97, 52);
            color: white;
            border: none;
        }
    `;

    const reportHTML = `
        <!DOCTYPE html>
            <html lang="en">
            <head>
            <title>CSS Template</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
        ${style}
        </style>
        </head>
        <body>
        <div class="container-table100">
        <img style="width: 60%;" src="https://camo.githubusercontent.com/39f67c9a861833fdb250d7b56e8fcb4922a9c0106c70dcf6f45fda2004312ed4/68747470733a2f2f692e696d6775722e636f6d2f48355664364b492e706e67">
			<div class="wrap-table100">
                <div class="table100 ver5">
                <div class="table100-head">
                    <table>
                        <thead>
                            <tr class="head">
                                <th class="column1">Select behaviors to disable.</th>
                                <th class="column2">Confidence</th>
                            </tr>
                        </thead>
                    </table>
                </div>

                <div class="table100-body">
                    <table>
                        <tbody>
                        ${allCrimesHTML}
                        </tbody>
                    </table>
                </div>
                </div>
                <button class="rebuild-btn" onclick="submit()">Rebuild</button>
			</div>
        </div>
    </body>
    </html>
    <script>
    const vscode = acquireVsCodeApi();

    function checkBoxClick(id){
        var checkbox = document.getElementById(id).querySelectorAll("input")
        checkbox[0].click()
    }

    function submit(){
        var checkboxs = document.getElementsByName("rebuild-check")

        var selectedCrimes = []
        checkboxs.forEach(element => {
            if (element.checked){
                selectedCrimes.push(element.value)
            }
        });
      
        vscode.postMessage({
            command: 'rebuild',
            crimes: selectedCrimes
        });
    }
    </script>
`;
    return reportHTML;
}
