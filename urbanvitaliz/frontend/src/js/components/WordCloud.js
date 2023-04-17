import Alpine from 'alpinejs'
import * as d3 from "d3";
import * as cloud from "d3-cloud"

console.log('cloud', cloud);

function WordCloud(wordsData) {
    return {
        init() {

            const jsonWords = JSON.parse(wordsData.textContent)

            const wordsReadyForClouds = Object.entries(jsonWords).map((entry) => {
                const [key, value] = entry;
                return {
                    text:key,
                    size:value*15
                }
            });

            const fill = d3.scaleOrdinal(d3.schemeCategory10);

            const layout = cloud()
                .size([800, 600])
                .words(wordsReadyForClouds)
                .padding(1)
                .rotate(function () { return ~~(Math.random() * 2) * 90; })
                .font("Impact")
                .fontSize(function (d) { return d.size; })
                .on("end", draw);

            layout.start();

            function draw(words) {
                d3.select("#wordCloud").append("svg")
                    .attr("width", layout.size()[0])
                    .attr("height", layout.size()[1])
                  .append("g")
                    .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
                  .selectAll("text")
                    .data(words)
                  .enter().append("text")
                    .attr('class', 'is-word')
                    .style("font-size", function(d) { return d.size + "px"; })
                    .style("font-family", "Impact")
                    .style("fill", function(d, i) { return fill(i); })
                    .attr("text-anchor", "middle")
                    .attr("transform", function(d) {
                      return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                    }).append('a')
                    .attr('href',function(d) { return 'http://urbanvitaliz.localhost:8000/crm/tag/' + d.text })
                    .style('text-decoration', 'none')
                    .text(function(d) { return d.text; });
              }
        },

    }
}

Alpine.data("WordCloud", WordCloud)
